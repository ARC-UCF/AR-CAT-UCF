import string

FIRST = 1

class Identifier():
    def __init__(self):
        self.nextTrackId = None
        
    def issue_identifier(self):
        
        if self.nextTrackId is None: self.nextTrackId = FIRST
        
        oldIdentifier = self.nextTrackId
        
        self.nextTrackId = self.increment_id(self.nextTrackId)
        
        return oldIdentifier
        
    def increment_id(self, id):
        id += 1
        return id
    
    def write_to_id(self, id):
        self.nextTrackId = int(id)
            
    def provide_next_id(self) -> str:
        return self.nextTrackId
        
identifier = Identifier()