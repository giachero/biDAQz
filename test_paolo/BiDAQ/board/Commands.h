#ifndef __COMMANDS_H
#define	__COMMANDS_H
/* Do not add comments with '//' or change numbers 'x.' otherwise they are interpreted wrongly by the MATLAB GUI */

// 1. Payload format
#define	CAN_CMD_QUEUE_STATUS_BYTE		(CAN_CMD_DATA_LENGTH-1)
#define	CAN_CMD_DATA_BYTE_END				(CAN_CMD_QUEUE_STATUS_BYTE-1)

// 2. Queue
#define	CAN_CMD_QUEUE_OFF						0x00
#define	CAN_CMD_QUEUE_ON						0x01

// 3. Return commands
#define	CAN_CMD_NOT_IMPLEMENTED			0xF8
#define	CAN_CMD_WARNING							0xF9
#define	CAN_CMD_WRONG_CHANNEL				0xFA
#define	CAN_CMD_WRONG_ARG						0xFB
#define	CAN_CMD_UNKNOWN_CMD					0xFC
#define	CAN_CMD_QUEUE_FULL					0xFD
#define	CAN_CMD_BUSY								0xFE
#define	CAN_CMD_ERROR								0xFF

// 4. Read command
#define	CAN_CMD_READ										0x80

// 5.1. Generic commands
#define	CAN_CMD_NOP											0x00																							//

#define	CAN_CMD_ID_WRITE								0x50																							//
#define	CAN_CMD_ID_READ									(CAN_CMD_ID_WRITE | CAN_CMD_READ)									// 3:4,1,'hex','hexadecimal',3:4,1,'num','decimal'
#define	CAN_CMD_FW_VER_READ							(0x51 | CAN_CMD_READ)															// 1:4,1,'num','YYMMDDhhmm'
#define CAN_CMD_HW_REV_READ							(0x52 | CAN_CMD_READ)															// 4:4,1,'num',''
#define	CAN_CMD_BLINK										0x5F																							// 

#define	CAN_CMD_RESTART									0x70																							//
#define	CAN_CMD_RECALIBRATE							0x71																							//
#define	CAN_CMD_POWERDOWN_CONFIG				0x72																							// 
#define	CAN_CMD_POWERDOWN_READ					(CAN_CMD_POWERDOWN_CONFIG | CAN_CMD_READ)					// 4:4,1,'bool','true = enabled\nfalse = disabled'
#define	CAN_CMD_RESET_FACTORY						0x78																							//

// 5.2. Filter commands
#define	CAN_CMD_FILTER_ENABLE_WRITE			0x01																							//
#define	CAN_CMD_FILTER_ENABLE_READ			(CAN_CMD_FILTER_ENABLE_WRITE | CAN_CMD_READ)			// 3:4,1,'hex','1 = enabled\n0 = bypass'
#define	CAN_CMD_FREQUENCY_WRITE					0x02																							// 1:4,1,'num','Hz'
#define	CAN_CMD_FREQUENCY_READ					(CAN_CMD_FREQUENCY_WRITE | CAN_CMD_READ)					// 1:4,1,'num','Hz'
#define	CAN_CMD_INPUT_GROUND_WRITE			0x03																							//
#define	CAN_CMD_INPUT_GROUND_READ				(CAN_CMD_INPUT_GROUND_WRITE | CAN_CMD_READ)				// 3:4,1,'hex','1 = grounded\n0 = normal'
#define	CAN_CMD_FREQUENCY_AND_ENABLE		0x04																							// 1:4,1,'num','Hz'
#define	CAN_CMD_TRIMMER_WRITE						0x0E																							//  
#define	CAN_CMD_TRIMMER_READ						(CAN_CMD_TRIMMER_WRITE | CAN_CMD_READ)						// 3:4,1,'hex',''
#define	CAN_CMD_TRIMMER_READ_FORCE			(0x0F | CAN_CMD_READ)															// 3:4,1,'hex',''

// 5.3. Memory commands
#define	CAN_CMD_LOAD_SETTINGS						0x10																							//
#define	CAN_CMD_SAVE_SETTINGS						0x11																							//
#define	CAN_CMD_SLOT_LOCK_WRITE					0x12																							//
#define	CAN_CMD_SLOT_LOCK_READ					(CAN_CMD_SLOT_LOCK_WRITE | CAN_CMD_READ)					// 4:4,1,'bool','true = lock\nfalse = unlock'
#define	CAN_CMD_SLOT_USED_WRITE					0x13																							//
#define	CAN_CMD_SLOT_USED_READ					(CAN_CMD_SLOT_USED_WRITE | CAN_CMD_READ)					// 4:4,1,'bool','true = used\nfalse = unused'
#define	CAN_CMD_SLOT_STARTUP_WRITE			0x14																							//
#define	CAN_CMD_SLOT_STARTUP_READ				(CAN_CMD_SLOT_STARTUP_WRITE | CAN_CMD_READ)				// 4:4,1,'num','0 = default settings\n1:7 = user settings'
#define	CAN_CMD_LOAD_STARTUP_SETTINGS		0x15																							//
#define	CAN_CMD_MEMORY_WRITE						0x18																							//
#define	CAN_CMD_MEMORY_READ							(CAN_CMD_MEMORY_WRITE | CAN_CMD_READ)							// 1:4,1,'hex',''
#define	CAN_CMD_ERASE_ALL								0x1F																							//

// 5.4. ADC commands
#define	CAN_CMD_ADC_MEAS_EN_WRITE				0x20																							//
#define	CAN_CMD_ADC_MEAS_EN_READ				(CAN_CMD_ADC_MEAS_EN_WRITE | CAN_CMD_READ)				// 4:4,1,'bool','true = enabled\nfalse = disabled'
#define	CAN_CMD_ADC_FREQ_WRITE					0x21																							// 1:4,1000,'num','Hz'
#define	CAN_CMD_ADC_FREQ_READ						(CAN_CMD_ADC_FREQ_WRITE | CAN_CMD_READ)						// 1:4,1000,'num','Hz'
#define	CAN_CMD_ADC_ACQ_TIME_WRITE			0x22																							//
#define	CAN_CMD_ADC_ACQ_TIME_READ				(CAN_CMD_ADC_ACQ_TIME_WRITE | CAN_CMD_READ)				// 3:4,1,'num','ms'
#define	CAN_CMD_ADC_REG_WRITE						0x28																							//
#define	CAN_CMD_ADC_REG_READ						(CAN_CMD_ADC_REG_WRITE | CAN_CMD_READ)						// 1:4,1,'hex',''
#define	CAN_CMD_ADC_SHORT_INPUTS_WRITE	0x29																							//
#define	CAN_CMD_ADC_SHORT_INPUTS_READ		(CAN_CMD_ADC_SHORT_INPUTS_WRITE | CAN_CMD_READ)		// 4:4,1,'bool','true = shorted\nfalse = normal'
#define	CAN_CMD_ADC_BUFFERS_WRITE				0x2A																							//
#define	CAN_CMD_ADC_BUFFERS_READ				(CAN_CMD_ADC_BUFFERS_WRITE | CAN_CMD_READ)				// 4:4,1,'bool','true = enabled\nfalse = disabled'
#define	CAN_CMD_ADC_REF_BUFFERS_WRITE		0x2B																							//
#define	CAN_CMD_ADC_REF_BUFFERS_READ		(CAN_CMD_ADC_REF_BUFFERS_WRITE | CAN_CMD_READ)		// 4:4,1,'bool','true = enabled\nfalse = disabled'
#define	CAN_CMD_ADC_CALIBRATION_WRITE		0x2D																							//
#define	CAN_CMD_ADC_CALIBRATION_READ		(CAN_CMD_ADC_CALIBRATION_WRITE | CAN_CMD_READ)		// 1:4,1,'hex','ADC value'
#define	CAN_CMD_ADC_CALIBRATION_SAVE		0x2E																							//
#define	CAN_CMD_ADC_CALIBRATION_RECALL	(CAN_CMD_ADC_CALIBRATION_SAVE | CAN_CMD_READ)			//
#define	CAN_CMD_ADC_CALIBRATION_AUTO		0x2F																							// 1:4,1,'hex','ADC value'

// 5.5. DAQ Command
#define	CAN_CMD_ADC_START_MEAS					0x38																							//
#define	CAN_CMD_ADC_STOP_MEAS						0x39																							//
#define	CAN_CMD_ADC_READ_MEAS						(0x3A | CAN_CMD_READ)															// 1:4,1,'meas',{'uV' 'uV RMS' 'uV' '' 'N. of samples' 'ms' ''}
#define	CAN_CMD_ADC_READ_DATA						(0x3B | CAN_CMD_READ)															//
#define	CAN_CMD_ADC_CONTINUOUS					0x3D																							//
#define	CAN_CMD_ADC_STOP								0x3E																							//
#define	CAN_CMD_ADC_SINGLE							0x3F																							// 1:4,1,'hex','ADC value',1:4,0.000001,'adcvolt','uV'
#define	CAN_CMD_MODE_WRITE							0x30																							//
#define	CAN_CMD_MODE_READ								(CAN_CMD_MODE_WRITE | CAN_CMD_READ)								// 4:4,1,'num','0 = Internal\n1 = Ext. serial\n2 = Ext. parallel'

// 5.6. Monitoring commands
#define	CAN_CMD_POWERSUPPLY_READ				(0x40 | CAN_CMD_READ)															// 3:4,1000,'signedfloat','V'
#define	CAN_CMD_TEMPERATURE_READ				(0X41 | CAN_CMD_READ)															// 3:4,100,'float','�C'
#define	CAN_CMD_TESTPOINT_READ					(0x4E | CAN_CMD_READ)															// 2:4,1,'hex','ADC value',1:1,1,'num','Iterations'
#define	CAN_CMD_TRIMMER_RES_READ				(0x4F | CAN_CMD_READ)															// 1:2,500,'float','kOhm',3:4,500,'float','kOhm'

// 5.7. Error commands
#define	CAN_CMD_ERROR_CNT_RESET					0x60																							//
#define	CAN_CMD_ERROR_CNT_READ					(CAN_CMD_ERROR_CNT_RESET | CAN_CMD_READ)					// 1:4,1,'num',''
#define	CAN_CMD_ERROR_LIST_RESET				0x61																							//
#define	CAN_CMD_ERROR_LIST_READ					(CAN_CMD_ERROR_LIST_RESET | CAN_CMD_READ)					// 1:1,1,'error','',4:4,1,'error',''
#define	CAN_CMD_ERROR_INSTANT_MODE			0x6F																							//
#define	CAN_CMD_ERROR_INSTANT_MODE_READ	(CAN_CMD_ERROR_INSTANT_MODE | CAN_CMD_READ)				// 4:4,1,'bool','true = enabled\nfalse = disabled'

// 6. Error reply
#define	CAN_CMD_ERROR_REPLY							(0x7F | CAN_CMD_READ)															//
#define	CAN_CMD_DATA_REPLY							(0x7E | CAN_CMD_READ)															// 1:4,1,'hex',''

#endif
