import u3

DEBUG_ONE_WIRE = False
DEBUG_DEVICE_COM = False

def oneWire(sense_pin, rom_function, rom_id, num_rx, tx_data = [], options = None, dpu_pin = 0):
	# Initialize Command variable
	command = []

	# As per 1-Wire Documentation page: 
	# http://labjack.com/support/u6/users-guide/5.2.23

	command.append(0) # Checksum8
	command.append(0xF8)
	command.append(0x1D)
	command.append(0x3C)
	command.append(0) # Checksum16 (LSB)
	command.append(0) # Checksum16 (MSB)

	# Configure Options
	options_val = 0
	if options is not None:
		if options.has_key('dpu_control_enable'):
			if options.dpu_control_enable:
				options_val |= 1
		if options.has_key('dpu_polarity'):
			if options.dpu_polarity:
				options_val |= 1 << 1
		if options.has_key('dpu_idle'):
			if options.dpu_idle:
				options_val |= 1 << 2

	command.append(options_val) # Options Byte
	command.append(0) # Reserved
	command.append(sense_pin)
	command.append(dpu_pin)
	command.append(0) # Reserved
	command.append(rom_function)

	# Invert romID, so data is LSB -> MSB
	inverted_rom_id = list(reversed(rom_id))
	# use command.extend([1,2]) to add to array...
	command.extend(inverted_rom_id)

	command.append(0) # Reserved
	command.append(len(tx_data))
	
	command.append(0) # Reserved
	command.append(num_rx)

	# Add tx_data to command array
	command.extend(tx_data)

	# Add tx_data padding to command array
	max_tx_data_index = 63
	min_tx_data_index = 24
	max_tx_data_length = max_tx_data_index - min_tx_data_index + 1
	unused_tx_data = (max_tx_data_length)-len(tx_data)
	blank_tx_data = [0] * unused_tx_data
	command.extend(blank_tx_data)

	

	if DEBUG_ONE_WIRE:
		print ""
		print " - Writing 1-Wire Data:", len(tx_data), ",",tx_data
		print " - ROM Id:", rom_id
		print " - ROM Function:", rom_function
		print " - Num Bytes Rx:", num_rx
	
	if DEBUG_DEVICE_COM:
		print ""
		print " - Write Command (", len(command), "):", command

	writeRes = d.write(command)

	# num_bytes_to_read = 12 # baseline number of bytes to read 0 -> 11
	# num_bytes_to_read += num_rx
	result = d.read(64) # read full packet (64 bytes) data

	error_code_index = 6
	warnings_index = 9
	data_start_index = 16

	error_code = result[error_code_index]
	warnings = result[warnings_index]
	all_read_data = result[data_start_index:]
	read_data = all_read_data[0:num_rx]

	if DEBUG_DEVICE_COM:
		print ""
		print " - Write Result:", writeRes
		print " - Read Result:", result
		print " - All Read Data:", all_read_data

	if DEBUG_ONE_WIRE:
		print ""
		print " - Read 1-Wire Data:", read_data

	if DEBUG_DEVICE_COM:
		print type(d.write)
		print type(d.read)
		print type(d._writeRead)

	# Return the read device data
	return read_data




# Open the device
d = u3.U3()

# 64 bit Sensor ROM ID MSB -> LSB
rom_id = [ 0xD8, 0x00, 0x00, 0x04, 0xCE, 0x1B, 0xAF, 0x28 ]

# DIO Pin Numbers are as follows
# 0 -> 7: FIO0 -> FIO7
# 8 -> 15: EIO0 -> EIO7
# 16 -> 19: CIO0 -> CIO7
dio_pin_number = 10 # EIO2
rom_function = 0x55 # Match function
num_bytes_rx = 8 # Read back 8 bytes of data
tx_data = [0xBE] # data to write to the sensor

# Perform Deivce IO
read_data = oneWire(dio_pin_number, rom_function, rom_id, num_bytes_rx, tx_data = tx_data)

print "Read 1-Wire Data:", read_data

# Close the device
d.close()