"""Read ordinary FTB SNBT, including newline-separated compounds and typed arrays."""
import json,re

class Reader:
    def __init__(self,text):self.s=text;self.i=0
    def ws(self):
        while self.i<len(self.s):
            if self.s[self.i].isspace() or self.s[self.i]==',':self.i+=1
            elif self.s.startswith('//',self.i):
                end=self.s.find('\n',self.i);self.i=len(self.s) if end<0 else end+1
            else:break
    def value(self):
        self.ws();c=self.s[self.i]
        if c=='{':
            self.i+=1;out={}
            while True:
                self.ws()
                if self.s[self.i]=='}':self.i+=1;return out
                if self.s[self.i] in ('"',"'"):key=self.string()
                else:
                    start=self.i
                    while self.s[self.i] not in ': \t\r\n':self.i+=1
                    key=self.s[start:self.i]
                self.ws();assert self.s[self.i]==':',(self.i,self.s[self.i:self.i+30]);self.i+=1
                out[key]=self.value()
        if c=='[':
            self.i+=1;out=[];self.ws()
            if self.i+1<len(self.s) and self.s[self.i] in 'BIL' and self.s[self.i+1]==';':self.i+=2
            while True:
                self.ws()
                if self.s[self.i]==']':self.i+=1;return out
                out.append(self.value())
        if c in ('"',"'"):return self.string()
        start=self.i
        while self.i<len(self.s) and self.s[self.i] not in ',]} \t\r\n':self.i+=1
        token=self.s[start:self.i]
        assert token,(self.i,self.s[self.i:self.i+40])
        if token in ('true','false'):return token=='true'
        if re.fullmatch(r'[-+]?\d+[bBsSlL]?',token):return int(re.sub('[bBsSlL]$','',token))
        if re.fullmatch(r'[-+]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][-+]?\d+)?[fFdD]?',token):return float(re.sub('[fFdD]$','',token))
        return token
    def string(self):
        quote=self.s[self.i];self.i+=1;out=''
        while self.i<len(self.s):
            c=self.s[self.i];self.i+=1
            if c==quote:return out
            if c=='\\':
                c=self.s[self.i];self.i+=1
                if c=='u':out+=chr(int(self.s[self.i:self.i+4],16));self.i+=4;continue
                out+=dict(n='\n',r='\r',t='\t').get(c,c)
            else:out+=c
        raise ValueError('Unterminated string')

def loads(text):
    r=Reader(text);value=r.value();r.ws();assert r.i==len(text),(r.i,text[r.i:r.i+50]);return value
