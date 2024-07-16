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
            "ecg.hr": (230, 40, 330, 110),
            "spo2.pr": (410, 50, 520, 120),
            "spo2.SpO2": (240, 190, 330, 245),
            "p1.sys": (245, 245, 300, 275),
            "p1.dia": (305, 245, 350, 275),
            "p1.mean": (260, 270, 330, 300),
            "co2.et": (245, 300, 320, 340),
            # "o2.et": (250, 350, 290, 385),
            # "o2.fi": (255, 370, 290, 400),
            "co2.rr": (380, 300, 450, 340),
            "aa.et": (385, 335, 425, 355),
            "aa.fi": (385, 350, 425, 370),
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
        "spo2.SpO2": [40, 100],
        "spo2.pr": [0, 160],
    }


OldMonitor()
HospitalMonitor()
