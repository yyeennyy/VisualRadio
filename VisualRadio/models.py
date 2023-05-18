from VisualRadio import db

class Wav(db.Model):
    
    broadcast = db.Column(db.String(20), nullable=False, default="None")
    radio_name = db.Column(db.String(50), primary_key=True)
    radio_date = db.Column(db.String(50), primary_key=True)
    raw = db.Column(db.Boolean, default=False)
    section = db.Column(db.Integer, nullable=False, default=0)
    stt = db.Column(db.Boolean, nullable=False, default=False)
    script = db.Column(db.Boolean, nullable=False, default=False)
    contents = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, broadcast, radio_name, radio_date, raw, section, stt, script, contents):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.raw = raw
        self.section = section
        self.stt = stt
        self.script = script
        self.contents = contents

    def __repr__(self):
        return f"<Radio {self.broadcast} {self.radio_name} {self.radio_date} : (raw : {self.raw}), (section: {self.section}), (stt: {self.stt}), (script: {self.script}), (contents: {self.contents}))>\n"

