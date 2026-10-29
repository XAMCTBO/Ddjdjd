package com.newbodymechanics.obdlogger

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.pm.PackageManager
import android.os.Build
import android.util.Base64
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import androidx.core.app.ActivityCompat
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.util.UUID
import java.util.concurrent.Executors

/**
 * Exposes classic Bluetooth (RFCOMM/SPP) and Bluetooth LE (GATT) to the JS
 * running in the WebView, under the JS-visible name "AndroidBT".
 *
 * JS calls (see obd-logger.html "native bridge" transport):
 *   AndroidBT.hasPermission(): boolean
 *   AndroidBT.requestPermission()
 *   AndroidBT.scan()                         -> results delivered via onDeviceFound(name, address, type)
 *   AndroidBT.stopScan()
 *   AndroidBT.connectClassic(address)        -> onConnected(address) / onConnectError(msg)
 *   AndroidBT.connectBle(address)            -> onConnected(address) / onConnectError(msg)
 *   AndroidBT.write(base64)                  -> raw bytes, classic socket or BLE write (whichever is active)
 *   AndroidBT.disconnect()
 *
 * Native -> JS callbacks (must exist as window.* functions in the page):
 *   onDeviceFound(name, address, type)   type = "classic" | "ble"
 *   onConnected(address)
 *   onConnectError(message)
 *   onData(base64)                       raw bytes received, phone -> page
 *   onDisconnected()
 *   onLog(message)                       free-text status/debug line
 */
class BtBridge(private val activity: Activity, private val webView: WebView) {

    private val TAG = "BtBridge"
    private val SPP_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    private val bg = Executors.newSingleThreadExecutor()

    private val adapter: BluetoothAdapter? by lazy {
        (activity.getSystemService(android.content.Context.BLUETOOTH_SERVICE) as BluetoothManager).adapter
    }

    private var classicSocket: BluetoothSocket? = null
    private var classicOut: OutputStream? = null
    private var classicIn: InputStream? = null
    private var readerRunning = false

    private var gatt: BluetoothGatt? = null
    private var gattWriteChar: BluetoothGattCharacteristic? = null

    // --- permissions -----------------------------------------------------------

    @JavascriptInterface
    fun hasPermission(): Boolean {
        val needed = permissionsNeeded()
        return needed.all {
            ActivityCompat.checkSelfPermission(activity, it) == PackageManager.PERMISSION_GRANTED
        }
    }

    @JavascriptInterface
    fun requestPermission() {
        ActivityCompat.requestPermissions(activity, permissionsNeeded(), 4201)
    }

    private fun permissionsNeeded(): Array<String> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(Manifest.permission.BLUETOOTH_CONNECT, Manifest.permission.BLUETOOTH_SCAN)
        } else {
            arrayOf(Manifest.permission.ACCESS_FINE_LOCATION)
        }
    }

    // --- scanning ----------------------------------------------------------------

    private val leScanCallback = object : ScanCallback() {
        @SuppressLint("MissingPermission")
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val name = result.device.name ?: "Unknown BLE device"
            emit("onDeviceFound", jsStr(name), jsStr(result.device.address), jsStr("ble"))
        }
    }

    @SuppressLint("MissingPermission")
    @JavascriptInterface
    fun scan() {
        val a = adapter ?: return emit("onConnectError", jsStr("Bluetooth not available on this device"))
        if (!hasPermission()) { emit("onConnectError", jsStr("Bluetooth permission not granted yet")); return }

        // Classic paired devices show up immediately.
        try {
            a.bondedDevices?.forEach { d ->
                emit("onDeviceFound", jsStr(d.name ?: "Unknown"), jsStr(d.address), jsStr("classic"))
            }
        } catch (e: SecurityException) { log("bondedDevices: ${e.message}") }

        try {
            a.bluetoothLeScanner?.startScan(leScanCallback)
            log("BLE scan started")
        } catch (e: Exception) { log("BLE scan failed: ${e.message}") }
    }

    @SuppressLint("MissingPermission")
    @JavascriptInterface
    fun stopScan() {
        try { adapter?.bluetoothLeScanner?.stopScan(leScanCallback) } catch (e: Exception) { }
    }

    // --- classic (RFCOMM/SPP) -----------------------------------------------------

    @SuppressLint("MissingPermission")
    @JavascriptInterface
    fun connectClassic(address: String) {
        bg.submit {
            try {
                val device = adapter?.getRemoteDevice(address)
                    ?: return@submit emit("onConnectError", jsStr("Adapter unavailable"))
                adapter?.cancelDiscovery()
                val socket = device.createRfcommSocketToServiceRecord(SPP_UUID)
                socket.connect()
                classicSocket = socket
                classicOut = socket.outputStream
                classicIn = socket.inputStream
                emit("onConnected", jsStr(address))
                startClassicReader()
            } catch (e: IOException) {
                emit("onConnectError", jsStr("Classic connect failed: ${e.message}"))
            }
        }
    }

    private fun startClassicReader() {
        readerRunning = true
        bg.submit {
            val buf = ByteArray(1024)
            while (readerRunning) {
                try {
                    val n = classicIn?.read(buf) ?: -1
                    if (n < 0) break
                    val b64 = Base64.encodeToString(buf, 0, n, Base64.NO_WRAP)
                    emit("onData", jsStr(b64))
                } catch (e: IOException) {
                    log("classic read ended: ${e.message}")
                    break
                }
            }
            readerRunning = false
            emit("onDisconnected")
        }
    }

    // --- BLE (GATT) ----------------------------------------------------------------

    // Known UART-bridge profiles used by common ELM327-clone dongles, same as the web app.
    private data class Profile(val service: UUID, val tx: UUID, val rx: UUID)
    private val profiles = listOf(
        Profile(
            UUID.fromString("6e400001-b5a3-f393-e0a9-e50e24dcca9e"),
            UUID.fromString("6e400002-b5a3-f393-e0a9-e50e24dcca9e"),
            UUID.fromString("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
        ),
        Profile(
            UUID.fromString("0000fff0-0000-1000-8000-00805f9b34fb"),
            UUID.fromString("0000fff2-0000-1000-8000-00805f9b34fb"),
            UUID.fromString("0000fff1-0000-1000-8000-00805f9b34fb")
        ),
        Profile(
            UUID.fromString("49535343-1e4d-4bd9-ba61-23c647249616"),
            UUID.fromString("49535343-8841-43f4-a8d4-ecbe34729bb3"),
            UUID.fromString("49535343-fe7d-4ae5-8fa9-9fafd205e455")
        )
    )
    private val CCCD: UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")

    @SuppressLint("MissingPermission")
    @JavascriptInterface
    fun connectBle(address: String) {
        val device = adapter?.getRemoteDevice(address)
            ?: return emit("onConnectError", jsStr("Adapter unavailable"))
        gatt = device.connectGatt(activity, false, object : BluetoothGattCallback() {
            @SuppressLint("MissingPermission")
            override fun onConnectionStateChange(g: BluetoothGatt, status: Int, newState: Int) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    g.discoverServices()
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    emit("onDisconnected")
                }
            }

            @SuppressLint("MissingPermission")
            override fun onServicesDiscovered(g: BluetoothGatt, status: Int) {
                var matched = false
                for (p in profiles) {
                    val svc = g.getService(p.service) ?: continue
                    val tx = svc.getCharacteristic(p.tx)
                    val rx = svc.getCharacteristic(p.rx)
                    if (tx != null && rx != null) {
                        gattWriteChar = tx
                        g.setCharacteristicNotification(rx, true)
                        val cccd = rx.getDescriptor(CCCD)
                        if (cccd != null) {
                            cccd.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                            g.writeDescriptor(cccd)
                        }
                        log("BLE matched known profile: ${p.service}")
                        matched = true
                        break
                    }
                }
                if (!matched) {
                    // generic fallback: first writable + notifiable characteristic found anywhere
                    outer@ for (svc in g.services) {
                        for (c in svc.characteristics) {
                            val writable = (c.properties and (BluetoothGattCharacteristic.PROPERTY_WRITE or BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE)) != 0
                            if (writable) gattWriteChar = c
                            val notifiable = (c.properties and BluetoothGattCharacteristic.PROPERTY_NOTIFY) != 0
                            if (notifiable) {
                                g.setCharacteristicNotification(c, true)
                                val cccd = c.getDescriptor(CCCD)
                                if (cccd != null) {
                                    cccd.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                                    g.writeDescriptor(cccd)
                                }
                            }
                            if (gattWriteChar != null && notifiable) { matched = true; break@outer }
                        }
                    }
                    if (matched) log("BLE generic fallback match")
                }
                if (!matched) {
                    emit("onConnectError", jsStr("No compatible BLE UART service found"))
                } else {
                    emit("onConnected", jsStr(address))
                }
            }

            override fun onCharacteristicChanged(g: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
                val bytes = characteristic.value ?: return
                emit("onData", jsStr(Base64.encodeToString(bytes, Base64.NO_WRAP)))
            }
        })
    }

    // --- shared write / disconnect ---------------------------------------------------

    @SuppressLint("MissingPermission")
    @JavascriptInterface
    fun write(base64: String) {
        val bytes = Base64.decode(base64, Base64.NO_WRAP)
        bg.submit {
            try {
                if (classicOut != null) {
                    classicOut?.write(bytes)
                    classicOut?.flush()
                } else if (gattWriteChar != null && gatt != null) {
                    gattWriteChar!!.value = bytes
                    gatt!!.writeCharacteristic(gattWriteChar)
                } else {
                    emit("onConnectError", jsStr("Not connected"))
                }
            } catch (e: Exception) {
                emit("onConnectError", jsStr("Write failed: ${e.message}"))
            }
        }
    }

    @SuppressLint("MissingPermission")
    @JavascriptInterface
    fun disconnect() {
        readerRunning = false
        try { classicSocket?.close() } catch (e: Exception) { }
        classicSocket = null; classicOut = null; classicIn = null
        try { gatt?.disconnect(); gatt?.close() } catch (e: Exception) { }
        gatt = null; gattWriteChar = null
        emit("onDisconnected")
    }

    // --- helpers ------------------------------------------------------------------

    private fun log(msg: String) {
        Log.d(TAG, msg)
        emit("onLog", jsStr(msg))
    }

    private fun jsStr(s: String): String = "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\""

    private fun emit(fn: String, vararg args: String) {
        val call = "javascript:(function(){ if(window.$fn) window.$fn(${args.joinToString(",")}); })();"
        activity.runOnUiThread { webView.evaluateJavascript(call, null) }
    }
}
