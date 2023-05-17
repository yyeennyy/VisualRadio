
from sqlalchemy import Column, String, Integer, Boolean
from init_db import Base


class Wav(Base):
    __tablename__ = 'Wav'
    
    broadcast = Column(String(20), nullable=False, default="None")
    radio_name = Column(String(50), primary_key=True)
    radio_date = Column(String(50), primary_key=True)
    raw = Column(Boolean, default=False)
    section = Column(Integer, nullable=False, default=0)
    stt = Column(Boolean, nullable=False, default=False)
    script = Column(Boolean, nullable=False, default=False)
    contents = Column(Boolean, nullable=False, default=False)

    def __init__(self, broadcast, radio_name, radio_date, raw, section=0, stt=False, script=False, contents=False):
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



