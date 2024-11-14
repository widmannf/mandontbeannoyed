class Color:
    def __init__(self, color_id):
        match int(color_id):
            case 0:
                self.color = 'white'
            case 1:
                self.color = 'grey'
            case 2:
                self.color = 'gold'
            case 3:
                self.color = 'darkgreen'
            case 4:
                self.color = 'darkred'
            case 5:
                self.color = 'bisque'
            case _:
                raise ValueError(f'Invalid color id: {color_id}')
    
    def __str__(self):
        return self.color