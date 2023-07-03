from VisualRadio import db
from sqlalchemy import ForeignKey


class Radio(db.Model):
    __tablename__ = 'radio'
    broadcast = db.Column(db.String(50), primary_key=True, index=True)
    radio_name = db.Column(db.String(50), primary_key=True, index=True)
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



class Wav(db.Model):
    
    broadcast = db.Column(db.String(50), ForeignKey('radio.broadcast', ondelete='CASCADE'), primary_key=True)
    radio_name = db.Column(db.String(50), ForeignKey('radio.radio_name', ondelete='CASCADE'), primary_key=True)
    radio_date = db.Column(db.String(50), primary_key=True, index=True)
    radio_section = db.Column(db.Text)

    def __init__(self, broadcast, radio_name, radio_date, radio_section):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.radio_section = radio_section

    def __repr__(self):
        return f"<Radio {self.broadcast} {self.radio_name} {self.radio_date}>\n"


class Listener(db.Model):
    __tablename__ = 'listener'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    broadcast = db.Column(db.String(50), ForeignKey('radio.broadcast', ondelete='CASCADE'))
    radio_name = db.Column(db.String(50), ForeignKey('radio.radio_name', ondelete='CASCADE'))
    radio_date = db.Column(db.String(50), ForeignKey('wav.radio_date', ondelete='CASCADE'))
    code = db.Column(db.Integer, nullable=False, primary_key=True)
    preview_text = db.Column(db.String(200), nullable=False, default="")
    time = db.Column(db.String(20), nullable=False, default="")

    def __init__(self, broadcast, radio_name, radio_date, code, preview_text, time):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.code = code
        self.preview_text = preview_text
        self.time = time
    
    def __repr__(self):
        return f"{self.code}"

class Process(db.Model):
    __tablename__ = 'process'
    broadcast = db.Column(db.String(50), ForeignKey('radio.broadcast', ondelete='CASCADE'), primary_key=True)
    radio_name = db.Column(db.String(50), ForeignKey('radio.radio_name', ondelete='CASCADE'), primary_key=True)
    radio_date = db.Column(db.String(50), ForeignKey('wav.radio_date', ondelete='CASCADE'), primary_key=True)
    raw = db.Column(db.Integer, nullable=False)
    split1 = db.Column(db.Integer, nullable=False)
    split2 = db.Column(db.Integer, nullable=False)
    end_stt = db.Column(db.Integer, nullable=False)
    all_stt = db.Column(db.Integer, nullable=False)
    script = db.Column(db.Integer, nullable=False)
    sum = db.Column(db.Integer, nullable=False)
    error = db.Column(db.Integer, nullable=False)

    def __init__(self, broadcast, radio_name, radio_date, raw, split1, split2, end_stt, all_stt, script, sum, error):
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
        self.error = error

    def __repr__(self):
        return f"Radio: {self.broadcast} {self.radio_name} {self.radio_date} : raw : {self.raw}, split1 : {self.split1}, split2 : {self.split2}, end_stt : {self.end_stt}, all_stt : {self.all_stt}, script : {self.script}, sum : {self.sum}"

class Keyword(db.Model):
    __tablename__ = 'keyword'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    broadcast = db.Column(db.String(50), ForeignKey('radio.broadcast', ondelete='CASCADE'))
    radio_name = db.Column(db.String(50), ForeignKey('radio.radio_name', ondelete='CASCADE'))
    radio_date = db.Column(db.String(50), ForeignKey('wav.radio_date', ondelete='CASCADE'))
    code = db.Column(db.String(10), nullable=False)
    keyword = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)


    def __init__(self, broadcast, radio_name, radio_date, code, keyword, time):
        self.broadcast = broadcast 
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.code = code
        self.keyword = keyword
        self.time = time