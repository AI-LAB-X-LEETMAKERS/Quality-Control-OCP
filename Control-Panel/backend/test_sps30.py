#!/usr/bin/env python3
"""
Standalone test script for Sensirion SPS30 dust sensor on Raspberry Pi.
Interface: /dev/serial0 (UART GPIO 14/15) at 115200 baud.
"""

import sys
import time

SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 115200

def main():
    print("=" * 60)
    print("       Sensirion SPS30 Dust Sensor Standalone Test")
    print(f"       Port: {SERIAL_PORT} | Baudrate: {BAUD_RATE}")
    print("=" * 60)

    # 1. Import dependencies
    try:
        from sensirion_shdlc_driver import ShdlcSerialPort
        from sensirion_driver_adapters.shdlc_adapter.shdlc_channel import ShdlcChannel
        from sensirion_uart_sps30.device import Sps30Device
        from sensirion_uart_sps30.commands import OutputFormat
    except ImportError as e:
        print(f"\n[ERROR] Missing required driver dependencies: {e}")
        print("Please run: pip install -r requirement.txt\n")
        sys.exit(1)

    # 2. Open serial connection
    print(f"\n[1/4] Connecting to SPS30 on {SERIAL_PORT}...")
    try:
        port = ShdlcSerialPort(port=SERIAL_PORT, baudrate=BAUD_RATE)
        channel = ShdlcChannel(port)
        sensor = Sps30Device(channel)
    except Exception as e:
        print(f"\n[FATAL] Failed to open {SERIAL_PORT}: {e}")
        print("\nTroubleshooting tips for /dev/serial0 on Raspberry Pi:")
        print("  1. Ensure UART is enabled: run 'sudo raspi-config'")
        print("     -> Interface Options -> Serial Port:")
        print("     -> Would you like a login shell over serial? NO")
        print("     -> Would you like serial port hardware enabled? YES")
        print("  2. Ensure your user has dialout permission:")
        print("     -> sudo usermod -a -G dialout $USER")
        print("  3. Check pin wiring:")
        print("     -> SPS30 Pin 1 (VDD) -> Pi Pin 2 or 4 (5V Power!)")
        print("     -> SPS30 Pin 2 (RX)  -> Pi Pin 8 (GPIO 14 / TX)")
        print("     -> SPS30 Pin 3 (TX)  -> Pi Pin 10 (GPIO 15 / RX)")
        print("     -> SPS30 Pin 4 (SEL) -> LEAVE DISCONNECTED (UART mode)")
        print("     -> SPS30 Pin 5 (GND) -> Pi Pin 6 (Ground)\n")
        sys.exit(1)

    try:
        # 3. Read Device Info
        product_type = sensor.get_product_type()
        serial_number = sensor.get_serial_number()
        print(f"[2/4] Device Detected!")
        print(f"      Product Type  : {product_type}")
        print(f"      Serial Number : {serial_number}")

        # 4. Start Measurement
        print("\n[3/4] Starting measurement (fan and laser on)...")
        sensor.start_measurement(OutputFormat.OUTPUT_FORMAT_FLOAT)
        print("      >>> SENSOR STARTED: Listen/feel for the fan spinning! <<<")
        print("      Waiting 3 seconds for airflow stabilization...")
        time.sleep(3.0)

        # 5. Continuous Reading Loop
        print("\n[4/4] Reading live particulate matter data (Press Ctrl+C to stop)...")
        print("-" * 65)
        print(f"{'Time':<10} | {'PM1.0':<8} | {'PM2.5':<8} | {'PM4.0':<8} | {'PM10':<8} | {'Unit'}")
        print("-" * 65)

        count = 0
        while True:
            # Check data ready flag if available
            ready = True
            if hasattr(sensor, "read_data_ready_flag"):
                try:
                    ready = sensor.read_data_ready_flag()
                except Exception:
                    ready = True
            elif hasattr(sensor, "get_data_ready_flag"):
                try:
                    ready = sensor.get_data_ready_flag()
                except Exception:
                    ready = True

            if ready:
                raw = sensor.read_measured_values()
                if isinstance(raw, (list, tuple)) and len(raw) >= 10:
                    pm1_0, pm2_5, pm4_0, pm10_0 = raw[0], raw[1], raw[2], raw[3]
                    typical_size = raw[9]
                elif hasattr(raw, "pm1p0"):
                    pm1_0 = raw.pm1p0.value
                    pm2_5 = raw.pm2p5.value
                    pm4_0 = raw.pm4p0.value
                    pm10_0 = raw.pm10p0.value
                    typical_size = raw.typical_particle_size.value
                else:
                    pm1_0, pm2_5, pm4_0, pm10_0 = raw[0], raw[1], raw[2], raw[3]
                    typical_size = raw[9]

                now = time.strftime("%H:%M:%S")
                print(f"{now:<10} | {pm1_0:>6.2f}   | {pm2_5:>6.2f}   | {pm4_0:>6.2f}   | {pm10_0:>6.2f}   | ug/m3  (size: {typical_size:.2f} um)")
                count += 1
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Waiting for new data...")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\nStopping measurement upon user request...")
    except Exception as e:
        print(f"\n[ERROR] An error occurred during measurement: {e}")
    finally:
        print("Powering down fan and laser...")
        try:
            sensor.stop_measurement()
            print("Sensor measurement stopped.")
        except Exception:
            pass
        try:
            port.close()
        except Exception:
            pass
        print("Done.")

if __name__ == "__main__":
    main()
