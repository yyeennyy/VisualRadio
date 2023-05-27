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



class Radio(db.Model):
    __tablename__ = 'radio'
    broadcast = db.Column(db.String(50), primary_key=True)
    radio_name = db.Column(db.String(50), primary_key=True)
    start_time = db.Column(db.String(50), nullable=True)
    record_len = db.Column(db.Integer, nullable=False, default=0)
    like_cnt = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, broadcast, radio_name, start_time, record_len, like_cnt):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.start_time = start_time
        self.record_len = record_len
        self.like_cnt = like_cnt

    def __repr__(self):
        return f"Radio: {self.broadcast} {self.radio_name}: 시작시간 {self.start_time}, 녹음시간 {self.record_len}"


class Listener(db.Model):
    __tablename__ = 'listener'
    broadcast = db.Column(db.String(50), primary_key=True)
    radio_name = db.Column(db.String(50), primary_key=True)
    radio_date = db.Column(db.String(50), primary_key=True)
    code = db.Column(db.Integer, nullable=False)

    def __init__(self, broadcast, radio_name, radio_date, code):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.start_time = radio_date
        self.code = code
    
    def __repr__(self):
        return f"청취자: {self.broadcast} {self.radio_name} {self.radio_date} => 청취자 {self.code}"

