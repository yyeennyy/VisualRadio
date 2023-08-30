from VisualRadio import db
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT

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
    start_times = db.Column(db.String(250))

    def __init__(self, broadcast, radio_name, radio_date, radio_section, start_times=""):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.radio_section = radio_section
        self.start_time = start_times

    def __repr__(self):
        return f"<Radio {self.broadcast} {self.radio_name} {self.radio_date}>\n"


class Listener(db.Model):
    __tablename__ = 'listener'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    broadcast = db.Column(db.String(50), ForeignKey('radio.broadcast', ondelete='CASCADE'))
    radio_name = db.Column(db.String(50), ForeignKey('radio.radio_name', ondelete='CASCADE'))
    radio_date = db.Column(db.String(50), ForeignKey('wav.radio_date', ondelete='CASCADE'))
    code = db.Column(db.Integer, nullable=False, primary_key=True)
    preview_text = db.Column(db.String(1000), nullable=False, default="")
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

    def __init__(self, broadcast, radio_name, radio_date):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.raw = 0
        self.split1 = 0
        self.split2 = 0
        self.end_stt = 0
        self.all_stt = 0
        self.script = 0
        self.sum = 0
        self.erorr = 0

    @property
    def raw_(self):
        return self.raw
    @property
    def split1_(self):
        return self.split1
    @property
    def split2_(self):
        return self.split2
    @property
    def end_stt_(self):
        return self.end_stt
    @property
    def all_stt_(self):
        return self.all_stt
    @property
    def script_(self):
        return self.script
    @property
    def sum_(self):
        return self.sum
    @property
    def error_(self):
        return self.error
    
    def set_raw(self):
        self.raw = 1
    def set_split1(self):
        self.split1 = 1
    def set_split2(self):
        self.split2 = 1
    def set_end_stt(self):
        self.end_stt = self.end_stt+1
    def set_all_stt(self, num):
        self.all_stt = num
    def set_script(self):
        self.script = 1
    def set_sum(self):
        self.sum = 1
    def set_error(self):
        self.error = 1
    def del_error(self):
        self.error = 0
    def del_stt(self):
        self.end_stt = 0

    def __repr__(self):
        return f"Radio: {self.broadcast} {self.radio_name} {self.radio_date} : raw : {self.raw}, split1 : {self.split1}, split2 : {self.split2}, end_stt : {self.end_stt}, all_stt : {self.all_stt}, script : {self.script}, sum : {self.sum}"

# 현재 얘는 청취자 사연 code, keyword로 사용중
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


# 현재 얘는 전체 스크립트에 대한 문단정보, 문단키워드 얘기임..
# 뭔가 청취자 키워드랑 통합할 필요 있음
# 일단 기능구현 후 DB 갈아엎기에 대한 고민 시작하자.
class Contents(db.Model):
    __tablename__ = 'contents'
    broadcast = db.Column(db.String(50), ForeignKey('radio.broadcast', ondelete='CASCADE'), primary_key=True)
    radio_name = db.Column(db.String(50), ForeignKey('radio.radio_name', ondelete='CASCADE'), primary_key=True)
    radio_date = db.Column(db.String(50), ForeignKey('wav.radio_date', ondelete='CASCADE'), primary_key=True)
    time = db.Column(db.String(20), primary_key=True)
    content = db.Column(LONGTEXT)
    keyword = db.Column(db.String(20), nullable=False, default="", primary_key=True)
    link = db.Column(db.String(500), default="None")
    
    def __init__(self, broadcast, radio_name, radio_date, time, content, keyword, link):
        self.broadcast = broadcast
        self.radio_name = radio_name
        self.radio_date = radio_date
        self.time = time
        self.content = content
        self.keyword = keyword
        self.link = link
    
    def __repr__(self):
        return f"{self.code}"