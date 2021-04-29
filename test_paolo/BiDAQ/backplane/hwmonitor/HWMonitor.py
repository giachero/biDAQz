try:
    from .sensors import sensors
except ImportError:
    pass


class HWMonitor:

    # Class constructor
    def __init__(self, VoltageThreshold=0.1, TempThreshold=80, FanThreshold=0):

        sensors.init()
        for Chip in sensors.iter_detected_chips():
            if str(Chip) == 'lm96080-i2c-0-29':
                self.HWMon = Chip
                break

        self.VoltageThreshold = VoltageThreshold
        self.TempThreshold = TempThreshold
        self.FanThreshold = FanThreshold

    def __del__(self):
        sensors.cleanup()

    def ReadSensors(self):

        Ret = dict()

        for Feature in self.HWMon:

            Value = Feature.get_value()
            Label = Feature.label

            if "/2" in Label:
                Value = Value * 2
                Label = Label.replace("/2", "")

            Ret[Label] = Value

        return Ret

    def IsPowerGood(self):

        SensorResults = self.ReadSensors()

        PowerGood = True

        for Key in SensorResults:
            if "Fan" in Key:
                LowThr = self.FanThreshold
                HighThr = float('inf')
            elif "Temp" in Key:
                LowThr = float('-inf')
                HighThr = self.TempThreshold
            else:
                ExpValue = float(Key[Key.find('(')+1:Key.rfind('V)')])
                LowThr = ExpValue * (1 - self.VoltageThreshold)
                HighThr = ExpValue * (1 + self.VoltageThreshold)

            MeasValue = float(SensorResults[Key])
            if (MeasValue < LowThr) | (MeasValue > HighThr):
                PowerGood = False

        return PowerGood, SensorResults
