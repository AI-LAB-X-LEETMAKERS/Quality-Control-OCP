#!/usr/bin/env python3
"""
Standalone test script for Sensirion SPS30 dust sensor on Raspberry Pi.
Interface: /dev/serial0 (UART GPIO 14/15) at 115200 baud.
"""

import sys
import time

SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 115200

def extract_val(item):
    if hasattr(item, "value"):
        return float(item.value)
    return float(item)

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
        try:
            from sensirion_uart_sps30.commands import OutputFormat
        except ImportError:
            OutputFormat = None
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
        # 3. Read Device Info safely
        product_name = "SPS30"
        serial_number = "Unknown"

        for method in ["get_product_name", "get_product_type", "read_product_type"]:
            if hasattr(sensor, method):
                try:
                    product_name = getattr(sensor, method)()
                    break
                except Exception:
                    pass

        for method in ["get_serial_number", "read_serial_number"]:
            if hasattr(sensor, method):
                try:
                    serial_number = getattr(sensor, method)()
                    break
                except Exception:
                    pass

        print(f"[2/4] Device Connected!")
        print(f"      Product : {product_name}")
        print(f"      Serial  : {serial_number}")

        # Print all available driver methods for transparency
        avail = [m for m in dir(sensor) if not m.startswith("_")]
        print(f"      Driver Methods: {', '.join(avail)}")

        # 4. Start Measurement
        print("\n[3/4] Starting measurement (fan and laser on)...")
        if OutputFormat and hasattr(OutputFormat, "OUTPUT_FORMAT_FLOAT"):
            sensor.start_measurement(OutputFormat.OUTPUT_FORMAT_FLOAT)
        else:
            sensor.start_measurement()

        print("      >>> SENSOR STARTED: Fan should be spinning now! <<<")
        print("      Waiting 3 seconds for airflow stabilization...")
        time.sleep(3.0)

        # Find the read method
        read_method_name = None
        for candidate in ["read_measured_values_float", "read_measured_values", "read_measured_values_ticks"]:
            if hasattr(sensor, candidate):
                read_method_name = candidate
                break

        print(f"      Using read method: sensor.{read_method_name}()")

        # 5. Continuous Reading Loop
        print("\n[4/4] Reading live particulate matter data (Press Ctrl+C to stop)...")
        print("-" * 65)
        print(f"{'Time':<10} | {'PM1.0':<8} | {'PM2.5':<8} | {'PM4.0':<8} | {'PM10':<8} | {'Unit'}")
        print("-" * 65)

        count = 0
        while True:
            # Check data ready flag if available
            ready = True
            for flag_method in ["read_data_ready_flag", "get_data_ready_flag"]:
                if hasattr(sensor, flag_method):
                    try:
                        ready = getattr(sensor, flag_method)()
                        break
                    except Exception:
                        ready = True

            if ready and read_method_name:
                raw = getattr(sensor, read_method_name)()

                # Debug print for first reading
                if count == 0:
                    print(f"      [DEBUG] Raw reading type: {type(raw).__name__}")

                if isinstance(raw, (list, tuple)) and len(raw) >= 4:
                    pm1_0 = extract_val(raw[0])
                    pm2_5 = extract_val(raw[1])
                    pm4_0 = extract_val(raw[2])
                    pm10_0 = extract_val(raw[3])
                    typical_size = extract_val(raw[9]) if len(raw) >= 10 else 0.0
                else:
                    pm1_0 = extract_val(getattr(raw, "mass_concentration_pm1p0", getattr(raw, "pm1p0", 0.0)))
                    pm2_5 = extract_val(getattr(raw, "mass_concentration_pm2p5", getattr(raw, "pm2p5", 0.0)))
                    pm4_0 = extract_val(getattr(raw, "mass_concentration_pm4p0", getattr(raw, "pm4p0", 0.0)))
                    pm10_0 = extract_val(getattr(raw, "mass_concentration_pm10p0", getattr(raw, "pm10p0", 0.0)))
                    typical_size = extract_val(getattr(raw, "typical_particle_size", 0.0))

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
