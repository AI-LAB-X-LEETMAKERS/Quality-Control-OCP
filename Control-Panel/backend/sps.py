#!/usr/bin/env python3
"""
SPS30 test with the Sensirion sensirion_uart_sps30 driver, no data-ready flag.
Run:  python3 sps30_test2.py -p /dev/serial0
"""
import argparse
import time

from sensirion_shdlc_driver import ShdlcSerialPort
from sensirion_driver_adapters.shdlc_adapter.shdlc_channel import ShdlcChannel
from sensirion_uart_sps30.device import Sps30Device
from sensirion_uart_sps30.commands import OutputFormat

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--serial-port", default="/dev/serial0")
args = ap.parse_args()

with ShdlcSerialPort(port=args.serial_port, baudrate=115200,
                     additional_response_time=0.02) as port:
    sensor = Sps30Device(ShdlcChannel(port))

    try:
        sensor.stop_measurement()   # make sure we start from idle
    except Exception:
        pass
    time.sleep(0.5)

    print("serial number:", sensor.read_serial_number())
    print("product type :", sensor.read_product_type())

    sensor.start_measurement(OutputFormat.OUTPUT_FORMAT_UINT16)
    print("Measurement started, fan should spin. Waiting 3 s...")
    time.sleep(3)

    try:
        for i in range(60):
            try:
                v = sensor.read_measurement_values_uint16()
                pm1, pm25, pm4, pm10 = v[0], v[1], v[2], v[3]
                size = v[9]
                print(f"{time.strftime('%H:%M:%S')}  PM1 {pm1}  PM2.5 {pm25}  "
                      f"PM4 {pm4}  PM10 {pm10} ug/m3  size {size}")
            except Exception as e:
                print("read error:", repr(e))
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        sensor.stop_measurement()
        print("Stopped.")