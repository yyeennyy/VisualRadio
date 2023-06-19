from VisualRadio import db

class Wav(db.Model):
    
    broadcast = db.Column(db.String(20), nullable=False, default="None", primary_key = True)
    radio_name = db.Column(db.String(50), primary_key=True)
    radio_date = db.Column(db.String(50), primary_key=True)

    def __init__(self, broadcast, radio_name, radio_date):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date

    def __repr__(self):
        return f"<Radio {self.broadcast} {self.radio_name} {self.radio_date}>\n"



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
    code = db.Column(db.Integer, nullable=False, primary_key=True)
    preview_text = db.Column(db.String(200), nullable=False, default="")

    def __init__(self, broadcast, radio_name, radio_date, code, preview_text):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.code = code
        self.preview_text = preview_text
    
    def __repr__(self):
        return f"청취자: {self.broadcast} {self.radio_name} {self.radio_date} => 청취자 {self.code}"

class Process(db.Model):
    __tablename__ = 'process'
    broadcast = db.Column(db.String(20), nullable=False, default="None", primary_key = True)
    radio_name = db.Column(db.String(50), primary_key=True)
    radio_date = db.Column(db.String(50), primary_key=True)
    raw = db.Column(db.Integer, nullable=False)
    split1 = db.Column(db.Integer, nullable=False)
    split2 = db.Column(db.Integer, nullable=False)
    end_stt = db.Column(db.Integer, nullable=False)
    all_stt = db.Column(db.Integer, nullable=False)
    script = db.Column(db.Integer, nullable=False)
    sum = db.Column(db.Integer, nullable=False)

    def __init__(self, broadcast, radio_name, radio_date, raw, split1, split2, end_stt, all_stt, script, sum):
        self.broadcast = broadcast 
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.raw = raw
        self.split1 = split1
        self.split2 = split2 
        self.end_stt = end_stt 
        self.all_stt = all_stt
        self.script = script
        self.sum = sum

    def __repr__(self):
        return f"Radio: {self.broadcast} {self.radio_name} {self.radio_date} : raw : {self.raw}, split1 : {self.split1}, split2 : {self.split2}, end_stt : {self.end_stt}, all_stt : {self.all_stt}, script : {self.script}, sum : {self.sum}"
