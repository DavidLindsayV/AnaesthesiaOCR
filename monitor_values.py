class Monitor:
    def __init__(self, field_pos):
        Monitor.field_pos = field_pos

        pos_centres = {}
        for key, value in Monitor.field_pos.items():
            pos_centres[key] = [
                (value[0] + value[2]) / 2,
                (value[1] + value[3]) / 2,
            ]
        Monitor.pos_centres = pos_centres

    def get_field_pos():
        return Monitor.field_pos

    def get_pos_centres():
        return Monitor.pos_centres


class OldMonitor(Monitor):

    def __init__(self):
        field_pos = {
            "ecg.hr": (500, 160, 580, 230),
            "co2.et": (465, 330, 510, 365),
            "co2.fi": (470, 365, 500, 390),
            "co2.rr": (500, 365, 530, 390),
            "p1.sys": (410, 400, 480, 430),
            "p1.dia": (480, 400, 530, 430),
            "p1.mean": (423, 430, 460, 450),
            "aa.et": (115, 400, 160, 425),
            "aa.fi": (120, 420, 160, 445),
        }

        super().__init__(field_pos)


class HospitalMonitor(Monitor):

    def __init__(self):
        field_pos = {
            "ecg.hr": (185, 35, 300, 125),
            "spo2.ir": (355, 35, 465, 115),
            "spo2.SpO2": (205, 190, 310, 260),
            "p1.sys": (220, 250, 280, 290),
            "p1.dia": (280, 250, 330, 290),
            "p1.mean": (240, 285, 300, 315),
            "co2.et": (220, 315, 290, 360),
            # "o2.et": (250, 350, 290, 385),
            # "o2.fi": (255, 370, 290, 400),
            "co2.rr": (360, 305, 440, 350),
            "aa.et": (370, 350, 415, 365),
            "aa.fi": (370, 365, 415, 385),
        }

        super().__init__(field_pos)


class Field_Ranges:
    field_ranges = {
        "ecg.hr": [180, 40],
        "co2.et": [60, 0],
        "co2.fi": [1, 0],
        "co2.rr": [35, 0],
        "p1.sys": [160, 50],
        "p1.dia": [120, 40],
        "p1.mean": [120, 50],
        "aa.et": [3, 0],
        "aa.fi": [5, 0],
        "spo2.SpO2": [40, 100]
    }


OldMonitor()
HospitalMonitor()
