#!/usr/bin/python

from .block import BoardControl
from .block import DataPacketizer
from .block import GeneralEnable
from .block import HpsToTxMac
from .block import ScFifo
from .block import SyncGenerator
from .block import TxMac
from .block import UdpStreamer
from .register import FpgaReg


class BiDAQFPGA:

	# Class constructor
	def __init__(self, BoardList=None):

		# Default value
		if BoardList is None:
			BoardList = list(range(0, 8))

		# Block classes init
		self.BoardControl = BoardControl.BoardControl(BoardList)
		self.DataPacketizer = DataPacketizer.DataPacketizer(BoardList)
		self.SyncGenerator = SyncGenerator.SyncGenerator(BoardList)
		self.UdpStreamer = UdpStreamer.UdpStreamer()
		self.GeneralEnable = GeneralEnable.GeneralEnable()
		self.TxMac = TxMac.TxMac()
		self.HpsToTxMac = HpsToTxMac.HpsToTxMac()
		self.FifoHpsMac = ScFifo.ScFifo("sc_fifo_hps_mac")
		self.FifoOutDataAdapter = ScFifo.ScFifo("fifo_adapter_data")
		self.FifoOutData = ScFifo.ScFifo("sc_fifo_data")
		self.FifoTxMac = ScFifo.ScFifo("sc_fifo_tx_eth_tse")
		self.LL = FpgaReg.FpgaReg(BoardList)
