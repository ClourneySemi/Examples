# Example for RTB2000 / RTM3000 / RTA4000 Oscilloscopes
# Preconditions:
# - Installed RsInstrument Python module Version 1.12.1.60 or newer from pypi.org
# - Installed VISA e.g. R&S Visa 5.12.x or newer

from RsInstrument import *  # The RsInstrument package is hosted on pypi.org, see Readme.txt for more details
from time import time

RsInstrument.assert_minimum_version('1.12.1.60')
rtb = None
try:
	# Adjust the VISA Resource string to fit your instrument
	rtb = RsInstrument('TCPIP::192.168.2.10::INSTR', True, False)
	rtb.visa_timeout = 3000  # Timeout for VISA Read Operations
	rtb.opc_timeout = 15000  # Timeout for opc-synchronised operations
	rtb.instrument_status_checking = True  # Error check after each command
except Exception as ex:
	print('Error initializing the instrument session:\n' + ex.args[0])
	exit()

print(f'RTB2000 IDN: {rtb.idn_string}')
print(f'RTB2000 Options: {",".join(rtb.instrument_options)}')

rtb.clear_status()
rtb.reset()

# -----------------------------------------------------------
# Basic Settings:
# ---------------------------- -------------------------------
rtb.write_str("TIM:ACQT 0.01")  # 10ms Acquisition time
rtb.write_str("CHAN1:RANG 5.0")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN1:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN1:COUP ACL")  # Coupling AC 1MOhm
rtb.write_str("CHAN1:STAT ON")  # Switch Channel 1 ON

# -----------------------------------------------------------
# Trigger Settings:
# -----------------------------------------------------------
rtb.write_str("TRIG:A:MODE AUTO")  # Trigger Auto mode in case of no signal is applied
rtb.write_str("TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")  # Trigger type Edge Positive
rtb.write_str("TRIG:A:SOUR CH1")  # Trigger source CH1
rtb.write_str("TRIG:A:LEV1 0.05")  # Trigger level 0.05V
rtb.query_opc()  # Using *OPC? query waits until all the instrument settings are finished

# -----------------------------------------------------------
# SyncPoint 'SettingsApplied' - all the settings were applied
# -----------------------------------------------------------
# Arming the SCOPE for single acquisition
# -----------------------------------------------------------
rtb.VisaTimeout = 2000  # Acquisition timeout - set it higher than the acquisition time
rtb.write_str("SING")
# -----------------------------------------------------------
# DUT_Generate_Signal() - in our case we use Probe compensation signal
# where the trigger event (positive edge) is reoccurring
# -----------------------------------------------------------
rtb.query_opc()  # Using *OPC? query waits until the instrument finished the Acquisition
# -----------------------------------------------------------
# SyncPoint 'AcquisitionFinished' - the results are ready
# -----------------------------------------------------------
# Fetching the waveform in ASCII and BINary format
# -----------------------------------------------------------
t = time()
trace = rtb.query_bin_or_ascii_float_list('FORM ASC;:CHAN1:DATA?')  # Query ascii array of floats
print(f'Instrument returned {len(trace)} points in the ascii trace, query duration {time() - t:.3f} secs')
t = time()
rtb.bin_float_numbers_format = BinFloatFormat.Single_4bytes  # This tells the driver in which format to expect the binary float data
trace = rtb.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN1:DATA?')  # Query binary array of floats - the query function is the same as for the ASCII format
print(f'Instrument returned {len(trace)} points in the binary trace, query duration {time() - t:.3f} secs')

# -----------------------------------------------------------
# Making an instrument screenshot and transferring the file to the PC
# -----------------------------------------------------------
rtb.write_str("MMEM:CDIR '/INT/'")  # Change the directory
rtb.InstrumentStatusChecking = False  # Ignore errors generated by the MMEM:DEL command, the error is generated if the file does not exist
rtb.write_str("MMEM:DEL 'Dev_Screenshot.png'")  # Delete the file if it already exists, otherwise you get 'Execution error' by creating a new screenshot
rtb.query_opc()
rtb.clear_status()
rtb.InstrumentStatusChecking = True  # Error checking back ON
rtb.write_str("HCOP:LANG PNG;:MMEM:NAME 'Dev_Screenshot'")  # Hardcopy settings for taking a screenshot - notice no file extension here
rtb.write_str("HCOP:IMM")  # Make the screenshot now
rtb.query_opc()  # Wait for the screenshot to be saved
rtb.read_file_from_instrument_to_pc(r'Dev_Screenshot.png', r'c:\Temp\PC_Screenshot.png')  # Query the instrument file to the PC
print(r"Screenshot file saved to PC 'c:\Temp\PC_Screenshot.png'")

# Close the session
rtb.close()
