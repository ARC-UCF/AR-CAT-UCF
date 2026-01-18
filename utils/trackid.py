import string
from config import identifierFormat

ALPHABET = string.ascii_uppercase + string.digits
BASE = len(ALPHABET)

class Identifier():
    def __init__(self):
        self.nextTrackId = None
        
        if identifierFormat.count("-") != 1:
            if identifierFormat.count("-") == 0:
                raise RuntimeError("A DASH MUST BE PRESENT IN THE IDENTIFIER FORMAT.")
            if identifierFormat.count("-") > 1:
                raise RuntimeError("MULTIPLE DASHES NOT SUPPORTED.")
        
        self.letChars = len(identifierFormat.split("-")[0])
        self.numChars = len(identifierFormat.split("-")[1])
        
    def issue_identifier(self):
        
        if self.nextTrackId is None: self.nextTrackId = identifierFormat
        
        oldIdentifier = self.nextTrackId
        
        self.nextTrackId = self.increment_id(self.nextTrackId)
        
        return oldIdentifier
        
    def _encode(self, num: int, length: int) -> str:
        s = []
        for _ in range(length):
            s.append(ALPHABET[num % BASE])
            num //= BASE
        return "".join(reversed(s))
    
    def _decode(self, code: str) -> int:
        num = 0
        for c in code:
            num = num * BASE + ALPHABET.index(c)
        return num
            
    def increment_id(self, id: str) -> int:
        num = self._decode(id.replace("-", ""))
        new_id = self._encode(num + 1, len(id.replace("-", "")))
        return new_id[:self.letChars] + "-" + new_id[self.letChars:]
    
    def write_to_id(self, id: str):
        if len(identifierFormat) == len(id):
            self.nextTrackId = id
            
    def provide_next_id(self) -> str:
        return self.nextTrackId
         
identifier = Identifier()