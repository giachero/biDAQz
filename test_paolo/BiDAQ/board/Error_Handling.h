//*********************************************************************
// Error_Handling.h
//---------------------------------------------------------------------
// This file contains the defines for the error codes and for the
// subsystem that generated them, toghether with the function
// prototypes and global variables definitions
//*********************************************************************

#ifndef __ERROR_HANDLING_H
#define __ERROR_HANDLING_H

#include "Bessel_Headers.h"

//*********************************************************************
// SPI subsystem
//---------------------------------------------------------------------
#define SPI_SUBSYS									0x01
#define	SPI_THREAD_OK								0x01
#define SPI_ERROR_WRONG_DATA_BITS		0x02
#define	SPI_ERROR_DRIVER						0x03
#define SPI_ERROR_OS_RELATED				0x04
#define SPI_ERROR_TIMEOUT						0x05
#define SPI_ERROR_DATA_LOST					0x06
#define SPI_ERROR_MODE_FAULT				0x07
#define SPI_ERROR_INIT							0x08
#define SPI_ERROR_PHASE_DIR					0x09
#define SPI_ERROR_PHASE_INV					0x0A

//*********************************************************************
// I2C subsystem
//---------------------------------------------------------------------
#define I2C_SUBSYS						0x02
#define I2C_OK								0x01
#define I2C_ERROR_INIT				0x02
#define I2C_ERROR_OS_RELATED	0x03
#define I2C_ERROR_TRANSFER		0x04
#define I2C_ERROR_DRIVER			0x05

//*********************************************************************
// Trimmer subsystem
//---------------------------------------------------------------------
#define TRIMMER_SUBSYS																			0x03
#define TRIMMER_OK																					0x01
#define TRIMMER_ERROR_SPI																		0x02					
#define TRIMMER_ERROR_CHAIN_POS_HIGHER_THAN_DEVICE_NUMBER 	0x03
#define TRIMMER_ERROR_WRITE_RDAC_READ_BACK_MISMATCH					0x04
#define TRIMMER_ERROR_SPI_MUTEX_TIMEOUT											0x05
#define TRIMMER_ERROR_HIGH_Z_CMD														0x06
#define TRIMMER_ERROR_READ_RDAC_CMD_WRITE										0x07
#define TRIMMER_ERROR_READ_RDAC_CMD_READ										0x08
#define	TRIMMER_ERROR_WRITE_RDAC_PROTECT_DISABLE						0x09
#define TRIMMER_ERROR_WRITE_RDAC_PROTECT_ENABLE							0x0A
#define	TRIMMER_ERROR_WRITE_RDAC_WRITE											0x0B
#define TRIMMER_ERROR_WRITE_RDAC_READ_BACK									0x0C
#define TRIMMER_ERROR_INIT																	0x0D
#define TRIMMER_ERROR_RESET																	0x0E

//*********************************************************************
// Port expander subsystem
//---------------------------------------------------------------------
#define PORT_EXPANDER_SUBSYS										0x04
#define PORT_EXPANDER_OK												0x01
#define PORT_EXPANDER_ERROR_GENERIC							0x02
#define PORT_EXPANDER_I2C_MUTEX_TIMEOUT 				0x03
#define PORT_EXPANDER_ERROR_PORT_VALUE					0x04
#define PORT_EXPANDER_ERROR_INIT_WRITE_OUTPUT		0x05
#define PORT_EXPANDER_ERROR_INIT_WRITE_CONFIG		0x06
#define PORT_EXPANDER_ERROR_READ_BIT						0x07
#define PORT_EXPANDER_ERROR_WRITE_READ					0x08
#define PORT_EXPANDER_ERROR_WRITE_PORT					0x09

//*********************************************************************
// Thermometer subsystem
//---------------------------------------------------------------------
#define THERMOMETER_SUBSYS												0x05
#define THERMOMETER_OK														0x01
#define THERMOMETER_ERROR_GENERIC									0x02
#define THERMOMETER_ERROR_I2C_MUTEX_TIMEOUT				0x03
#define	THERMOMETER_ERROR_INIT_WRITE_CFG					0x04
#define	THERMOMETER_ERROR_INIT_WRITE_CTRL					0x05
#define	THERMOMETER_ERROR_READ_TEMP_WRITE_CFG			0x06
#define	THERMOMETER_ERROR_READ_TMP_STATUS_TIMEOUT	0x07
#define	THERMOMETER_ERROR_READ_TMP_TIMEOUT				0x08

//*********************************************************************
// Memory subsystem
//---------------------------------------------------------------------
#define	MEMORY_SUBSYS										0x06
#define MEMORY_OK												0x01
#define MEMORY_ERROR_GENERIC						0x02
#define MEMORY_ERROR_I2C_MUTEX_TIMEOUT	0x03
#define MEMORY_ERROR_READBACK						0x04
#define MEMORY_ERROR_TIMEOUT_WRITE			0x05
#define MEMORY_ERROR_READ								0x06
#define MEMORY_ERROR_WRITE							0x07

//*********************************************************************
// Memory thread subsystem
//---------------------------------------------------------------------
#define	MEMORY_THREAD_SUBSYS											0x07
#define MEMORY_THREAD_OK													0x01
#define MEMORY_THREAD_ERROR_MUTEX_TIMEOUT					0x02
#define MEMORY_THREAD_ERROR_WRITE_QUEUE_TIMEOUT		0x03
#define MEMORY_THREAD_ERROR_WRITE									0x04
#define MEMORY_THREAD_ERROR_MEMPOOL_CLEAR					0x05
#define MEMORY_THREAD_ERROR_WRITE_MEMPOOL_UNAVAIL	0x06
#define MEMORY_THREAD_ERROR_READ_QUEUE_TIMEOUT		0x07
#define MEMORY_THREAD_ERROR_READ									0x08
#define MEMORY_THREAD_ERROR_READ_MEMPOOL_UNAVAIL	0x09
#define MEMORY_THREAD_ERROR_READ_SIZE							0x0A
#define MEMORY_THREAD_ERROR_OS_RELATED						0x0B

//*********************************************************************
// Memory (high level) subsystem
//---------------------------------------------------------------------
#define	MEMORY_HL_SUBSYS												0x08
#define	MEMORY_HL_OK														0x01
#define MEMORY_HL_ERROR_FORMAT									0x02
#define MEMORY_HL_ERROR_SAVE_SLOT_ENABLE_READ 	0x03
#define MEMORY_HL_ERROR_SAVE_SLOT_GROUND_READ 	0x04
#define MEMORY_HL_ERROR_SAVE_SLOT_UNAVAIL				0x05
#define MEMORY_HL_ERROR_SAVE_SLOT_WRITE					0x06
#define MEMORY_HL_ERROR_LOAD_SLOT_UNAVAIL				0x07
#define MEMORY_HL_ERROR_LOAD_SLOT_READ					0x08
#define MEMORY_HL_ERROR_LOCK_READ								0x09
#define MEMORY_HL_ERROR_SAVE_SLOT_LOCKED				0x0A
#define MEMORY_HL_ERROR_SLOT_LOCK								0x0B
#define MEMORY_HL_ERROR_LOAD_SLOT_WRITE_ENABLE	0x0C
#define	MEMORY_HL_ERROR_LOAD_SLOT_WRITE_GROUND	0x0D
#define MEMORY_HL_ERROR_LOAD_SLOT_WRITE_TRIMMER	0x0E
#define MEMORY_HL_ERROR_LOCK_READ_MEM_FREE			0x0F
#define MEMORY_HL_ERROR_USED_READ								0x10
#define MEMORY_HL_ERROR_USED_READ_MEM_FREE			0x11
#define MEMORY_HL_ERROR_USED_WRITE							0x12
#define MEMORY_HL_ERROR_USED_LOCKED							0x13
#define MEMORY_HL_ERROR_LOAD_STARTUP_READ				0x14
#define MEMORY_HL_ERROR_LOAD_SLOT_FREE_MEM			0x15

//*********************************************************************
// Relay driver subsystem
//---------------------------------------------------------------------
#define RELE_DRIVER_SUBSYS									0x09
#define RELE_DRIVER_OK											0x01
#define RELE_DRIVER_ERROR_GENERIC						0x02
#define	RELE_DRIVER_ERROR_SPI_WRITE					0x03
#define	RELE_DRIVER_ERROR_SPI_READ					0x04
#define RELE_DRIVER_ERROR_SPI_MUTEX_TIMEOUT	0x05
#define	RELE_DRIVER_ERROR_READBACK					0x06
#define RELE_DRIVER_ERROR_MEMORY_READ				0x07
#define RELE_DRIVER_ERROR_MEMORY_WRITE			0x08
#define	RELE_DRIVER_ERROR_MEMORY_BUSY				0x09
#define RELE_DRIVER_ERROR_INVALID_VAL				0x0A
#define RELE_DRIVER_ERROR_MEMORY_FREE_MEM		0x0B

//*********************************************************************
// ADC subsystem
//---------------------------------------------------------------------
#define ADC_SUBSYS													0x0A
#define ADC_OK															0x01
#define ADC_ERROR_GENERIC										0x02
#define ADC_ERROR_SPI_MUTEX_TIMEOUT					0x03
#define ADC_ERROR_SPI_COMMUNICATION_TIMEOUT	0x04
#define ADC_ERROR_GET_REG_INVALID_DEVICE		0x05
#define ADC_ERROR_READ_REG_INVALID_DEV			0x06
#define ADC_ERROR_READ_REG_READ							0x07
#define ADC_ERROR_READ_REG_CHECKSUM					0x08
#define ADC_ERROR_WRITE_REG_INVALID_DEV			0x09
#define ADC_ERROR_WRITE_REG_WRITE						0x0A
#define ADC_ERROR_RESET_INVALID_DEV					0x0B
#define ADC_ERROR_RESET_WRITE								0x0C
#define ADC_ERROR_WAIT_INVALID							0x0D
#define ADC_ERROR_WAIT_READ									0x0E
#define ADC_ERROR_READ_DATA_INVALID					0x0F
#define ADC_ERROR_READ_DATA_READ_REG				0x10
#define ADC_ERROR_UPD_CRC_INVALID						0x11
#define ADC_ERROR_SETUP_INVALID							0x12
#define ADC_ERROR_SETUP_RESET								0x13
#define ADC_ERROR_SETUP_ADC_MODE						0x14
#define ADC_ERROR_SETUP_IFMODE							0x15
#define ADC_ERROR_SETUP_CRC									0x16
#define ADC_ERROR_SETUP_WRITE_REG						0x17
#define ADC_ERROR_SETUP_READ_REG						0x18
#define ADC_ERROR_WAIT_TIMEOUT							0x19
#define ADC_ERROR_SETUP_DATA								0x1A

//*********************************************************************
// ADC (high level) subsystem
//---------------------------------------------------------------------
#define ADC_HL_SUBSYS												0x0B
#define ADC_HL_OK														0x01
#define ADC_HL_ERROR_INIT										0x02
#define ADC_HL_ERROR_POWER_UP								0x03
#define ADC_HL_ERROR_POWER_DOWN_GET_REG			0x04
#define ADC_HL_ERROR_POWER_DOWN							0x05
#define ADC_HL_ERROR_STANDBY_ON_GET_REG			0x06
#define ADC_HL_ERROR_STANDBY_ON							0x07
#define ADC_HL_ERROR_STANDBY_OFF_GET_REG		0x08
#define ADC_HL_ERROR_STANDBY_OFF						0x09
#define ADC_HL_ERROR_ADC_ENABLE_GET_REG			0x0A
#define ADC_HL_ERROR_ADC_ENABLE							0x0B
#define ADC_HL_ERROR_ADC_ENABLE_CH_GET_REG	0x0C
#define ADC_HL_ERROR_ADC_ENABLE_CH					0x0D
#define ADC_HL_ERROR_ADC_DISABLE_CH_GET_REG	0x0E
#define ADC_HL_ERROR_ADC_DISABLE_CH					0x0F
#define ADC_HL_ERROR_REG_SET_GET_REG				0x10
#define ADC_HL_ERROR_REG_SET_WRITE					0x11
#define ADC_HL_ERROR_REG_SET_READBACK				0x12
#define ADC_HL_ERROR_REG_CLR_GET_REG				0x13
#define ADC_HL_ERROR_REG_CLR_WRITE					0x14
#define ADC_HL_ERROR_REG_CLR_READBACK				0x15
#define ADC_HL_ERROR_REG_READ_INVALID_CHAN	0x16
#define ADC_HL_ERROR_REG_READ_GET_REG				0x17
#define ADC_HL_ERROR_REG_READ								0x18
#define ADC_HL_ERROR_CONTINUOUS							0x19
#define ADC_HL_ERROR_CONTINUOUS_GET_REG			0x1A
#define ADC_HL_ERROR_CONTINUOUS_READ_REG		0x1B
#define ADC_HL_ERROR_STOP_GET_REG						0x1C
#define ADC_HL_ERROR_STOP										0x1D
#define ADC_HL_ERROR_ZEROSCALE							0x1E
#define ADC_HL_ERROR_WRITE_FREQ							0x1F
#define ADC_HL_ERROR_READ_FREQ_INV_CHAN			0x20
#define ADC_HL_ERROR_READ_FREQ							0x21
#define ADC_HL_ERROR_READ_FREQ_GET_REG			0x22
#define ADC_HL_ERROR_WRITE_INPUT_SHORT			0x23
#define ADC_HL_ERROR_READ_INPUT_SHORT_INV_CHAN	0x24
#define ADC_HL_ERROR_READ_INPUT_SHORT						0x25
#define ADC_HL_ERROR_READ_INPUT_SHORT_GET_REG		0x26
#define ADC_HL_ERROR_INIT_GET_REG						0x27
#define ADC_HL_ERROR_INIT_WRONG_ID					0x28
#define ADC_HL_ERROR_STANDBY_ON_READBACK				0x29
#define ADC_HL_ERROR_OFFSET_INV_CHAN				0x2A
#define ADC_HL_ERROR_OFFSET									0x2B
#define ADC_HL_ERROR_OFFSET_GET_REG					0x2C
#define ADC_HL_ERROR_GAIN_INV_CHAN					0x2D
#define ADC_HL_ERROR_GAIN										0x2E
#define ADC_HL_ERROR_GAIN_GET_REG						0x2F
#define ADC_HL_ERROR_SINGLE_INV_CHAN				0x30
#define ADC_HL_ERROR_SINGLE_READ_FREQ				0x31
#define ADC_HL_ERROR_SINGLE_START						0x32
#define ADC_HL_ERROR_SINGLE_WAIT						0x33
#define ADC_HL_ERROR_SINGLE_GET_REG					0x34
#define ADC_HL_ERROR_SINGLE_READ_REG				0x35
#define ADC_HL_ERROR_SINGLE_WRONG_CHAN			0x36
#define ADC_HL_ERROR_SINGLE_ADC_ERR					0x37
#define ADC_HL_ERROR_SINGLE_DISABLE_CHAN		0x38
#define ADC_HL_ERROR_SINGLE_UV							0x39
#define ADC_HL_ERROR_ENABLE_MEAS_INV_CHAN		0x3A
#define ADC_HL_ERROR_ENABLE_MEAS						0x3B
#define ADC_HL_ERROR_GET_DATA_GET_REG				0x3C
#define ADC_HL_ERROR_GET_DATA_READ_REG			0x3D
#define ADC_HL_ERROR_GET_DATA_ADC_ERR				0x3E
#define ADC_HL_ERROR_CONTINUOUS_CONV				0x3F
#define ADC_HL_ERROR_WRITE_BUFFER_ENABLED							0x40
#define ADC_HL_ERROR_READ_BUFFER_ENABLED_INV_CHAN			0x41
#define ADC_HL_ERROR_READ_BUFFER_ENABLED							0x42
#define ADC_HL_ERROR_READ_BUFFER_ENABLED_GET_REG			0x43
#define ADC_HL_ERROR_WRITE_REF_BUFFER_ENABLED 				0x44
#define ADC_HL_ERROR_READ_REF_BUFFER_ENABLED_INV_CHAN	0x45
#define ADC_HL_ERROR_READ_REF_BUFFER_ENABLED					0x46
#define ADC_HL_ERROR_READ_REF_BUFFER_ENABLED_GET_REG	0x47

//*********************************************************************
// ADC thread subsystem
//---------------------------------------------------------------------
#define ADC_THREAD_SUBSYS									0x0C
#define ADC_THREAD_OK											0x01
#define ADC_THREAD_ERROR_FLAG							0x02
#define ADC_THREAD_ERROR_WAIT							0x03
#define ADC_THREAD_ERROR_READ_DATA				0x04
#define ADC_THREAD_ERROR_OS_RELATED				0x05
#define ADC_THREAD_ERROR_SETTER_PUT_MSG		0x06
#define ADC_THREAD_ERROR_SETTER_READ			0x07
#define ADC_THREAD_ERROR_START						0x08
#define ADC_THREAD_ERROR_STOP							0x09
#define ADC_THREAD_ERROR_SET_ENABLE				0x0A
#define ADC_THREAD_ERROR_SET_TIME					0x0B
#define ADC_THREAD_ERROR_GET_TIME					0x0C
#define ADC_THREAD_ERROR_GET_ENABLE				0x0D
#define ADC_THREAD_ERROR_GET_MEAN					0x0E
#define ADC_THREAD_ERROR_GET_RMS					0x0F
#define ADC_THREAD_ERROR_GET_CNT					0x10
#define ADC_THREAD_ERROR_GET_STATUS				0x11
#define ADC_THREAD_ERROR_GETTER_CHANNEL		0x12
#define ADC_THREAD_ERROR_GETTER_PUT_MSG		0x13
#define	ADC_THREAD_ERROR_GETTER_READ			0x14
#define ADC_THREAD_ERROR_START_SET_CONT		0x15
#define ADC_THREAD_ERROR_RETURN_QUEUE			0x16
#define ADC_THREAD_ERROR_STOP_CHANNEL			0x17
#define ADC_THREAD_ERROR_ENABLE_CHANNEL		0x18
#define ADC_THREAD_ERROR_GET_MAX_MIN			0x19

//*********************************************************************
// Power supply subsystem
//---------------------------------------------------------------------
#define POWER_SUPPLY_SUBSYS				0x0D
#define POWER_SUPPLY_OK						0x01
#define POWER_SUPPLY_RETURN_ERROR 0x02
#define POWER_SUPPLY_ERROR_MIN		0x0E
#define POWER_SUPPLY_ERROR_MAX		0x0F

//#define POWER_SUPPLY_ERROR_DIG_IN_MIN		0x0E
//#define POWER_SUPPLY_ERROR_DIG_MIN			0x1E
//#define POWER_SUPPLY_ERROR_MIC_MIN			0x2E
//#define POWER_SUPPLY_ERROR_ADC_MIN			0x3E
//#define POWER_SUPPLY_ERROR_ANA_IN_P_MIN	0x4E
//#define POWER_SUPPLY_ERROR_ANA_IN_N_MIN	0x5E
//#define POWER_SUPPLY_ERROR_ANA_P_MIN		0x6E
//#define POWER_SUPPLY_ERROR_ANA_N_MIN		0x7E
//#define POWER_SUPPLY_ERROR_DIG_IN_MAX		0x0F
//#define POWER_SUPPLY_ERROR_DIG_MAX			0x1F
//#define POWER_SUPPLY_ERROR_MIC_MAX			0x2F
//#define POWER_SUPPLY_ERROR_ADC_MAX			0x3F
//#define POWER_SUPPLY_ERROR_ANA_IN_P_MAX	0x4F
//#define POWER_SUPPLY_ERROR_ANA_IN_N_MAX	0x5F
//#define POWER_SUPPLY_ERROR_ANA_P_MAX		0x6F
//#define POWER_SUPPLY_ERROR_ANA_N_MAX		0x7F

//*********************************************************************
// Calibration subsystem
//---------------------------------------------------------------------
#define CALIBRATION_SUBSYS										0x0E
#define CALIBRATION_OK												0x01
#define CALIBRATION_ERROR_INV_MUX							0x02
#define CALIBRATION_ERROR_READ_INPUT_GND			0x03
#define CALIBRATION_ERROR_SET_INPUT_GND				0x04
#define CALIBRATION_ERROR_SET_TEST_SEL				0x05
#define CALIBRATION_ERROR_RESET_INPUT_GND			0x06
#define CALIBRATION_ERROR_RESET_TEST_SEL			0x07
#define CALIBRATION_ERROR_TP_READ_TL_EN				0x08
#define CALIBRATION_ERROR_TP_READ_TL_DIS			0x09
#define CALIBRATION_ERROR_TP_READ_ADC					0x0A
#define CALIBRATION_ERROR_TP_READ_FREQ				0x0B
#define CALIBRATION_ERROR_TP_READ_TIMEOUT			0x0C
#define CALIBRATION_ERROR_RES_READ_TP					0x0D
#define CALIBRATION_ERROR_OFFSET_WRONG_CHAN 	0x0E
#define CALIBRATION_ERROR_OFFSET_ADC_STOP			0x0F
#define CALIBRATION_ERROR_OFFSET_ADC_ENABLE		0x10
#define CALIBRATION_ERROR_OFFSET_SAVE_INPUT		0x11
#define CALIBRATION_ERROR_OFFSET_GROUND				0x12
#define CALIBRATION_ERROR_OFFSET_SAVE_FREQ		0x13
#define CALIBRATION_ERROR_OFFSET_WRITE_FREQ		0x14
#define CALIBRATION_ERROR_OFFSET_ADJ					0x15
#define CALIBRATION_ERROR_OFFSET_READ_VAL			0x16
#define CALIBRATION_ERROR_OFFSET_RESET_FREQ		0x17
#define CALIBRATION_ERROR_OFFSET_RESET_INPUT	0x18
#define CALIBRATION_ERROR_OFFSET_ADC_DISABLE	0x19
#define CALIBRATION_ERROR_OFFSET_SAVE_FILTER	0x1A
#define CALIBRATION_ERROR_OFFSET_READ_GAIN		0x1B
#define CALIBRATION_ERROR_OFFSET_WRITE_GAIN		0x1C			

//*********************************************************************
// LED subsystem
//---------------------------------------------------------------------
#define LED_SUBSYS							0x0F
#define LED_OK 									0x01
#define	LED_ERROR_MALLOC				0x02
#define LED_ERROR_START_THREAD	0x03

//*********************************************************************
// Initialization subsystem
//---------------------------------------------------------------------
#define INIT_SUBSYS									0x10
#define INIT_OK											0x01
#define INIT_ERROR_GPIO							0x02
#define INIT_ERROR_ADCMICRO					0x03
#define INIT_ERROR_TRIMMER					0x04
#define INIT_ERROR_RELE							0x05
#define INIT_ERROR_THERMOMETER			0x06
#define INIT_ERROR_PORTEXP					0x07
#define INIT_ERROR_TRIMMERCALI			0x08
#define INIT_ERROR_ADC							0x09
#define INIT_ERROR_MEMORY_FORMAT		0x0A
#define INIT_ERROR_LOAD_STARTUP			0x0B
#define INIT_ERROR_LOAD_ID					0x0C
#define INIT_ERROR_LOAD_POWERDOWN		0x0D
#define INIT_ERROR_LOAD_ERROR_MODE	0x0E
#define INIT_ERROR_ADC_CALIBRATION	0x0F
#define INIT_ERROR_ADC_THREAD				0x10

//*********************************************************************
// CAN bus subsystem
//---------------------------------------------------------------------
#define CAN_SUBSYS					0x11
#define CAN_OK							0x01
#define CAN_ERROR_INIT			0x02
#define CAN_ERROR_SEND			0x03
#define CAN_ERROR_RX_QUEUE	0x04
#define CAN_ERROR_TX_QUEUE	0x05

// Error structure typedef
typedef struct {
	int32_t Subsystem;
	int32_t	Error;
} Error_t;

// Global variables
extern uint32_t	gCounterErrors;
extern uint8_t	gError_Instant_Mode;
extern uint8_t	gError_Enable;

// Function prototypes
int32_t 	Init_Error_Handling	(void);
void 			Put_Error						(int32_t subsys, int32_t error);
Error_t *	Get_Error						(void);
int32_t 	Reset_Error					(void);

#endif
