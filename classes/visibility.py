class Visibility:

    def __init__(self, promotedToRecommended=-1, promotedToOwnHome=-1, promotedToSharedHome=-1):
        
        if promotedToRecommended == -1:
            self.promotedToRecommended = promotedToRecommended
        else:
            self.promotedToRecommended = 1 if promotedToRecommended else 0

        if promotedToOwnHome == -1:
            self.promotedToOwnHome = promotedToOwnHome
        else:
            self.promotedToOwnHome = 1 if promotedToOwnHome else 0

        if promotedToSharedHome == -1:
            self.promotedToSharedHome = promotedToSharedHome
        else:
            self.promotedToSharedHome = 1 if promotedToSharedHome else 0

    def to_dict(self):

        ret_val = {}

        if self.promotedToRecommended != -1:
            ret_val['promotedToRecommended'] = self.promotedToRecommended

        if self.promotedToOwnHome != -1:
            ret_val['promotedToOwnHome'] = self.promotedToOwnHome

        if self.promotedToSharedHome != -1:
            ret_val['promotedToSharedHome'] = self.promotedToSharedHome

        return ret_val

    def to_string(self):

        ret_val = ""

        if self.promotedToRecommended != -1:
            ret_val += 'Recomm='+str(self.promotedToRecommended)+" "

        if self.promotedToOwnHome != -1:
            ret_val += 'Home='+str(self.promotedToOwnHome)+" "

        if self.promotedToSharedHome != -1:
            ret_val += 'ShareHome='+str(self.promotedToSharedHome)+" "

        return ret_val

    @staticmethod
    def keys():
        return ['promotedToRecommended', 'promotedToOwnHome', 'promotedToSharedHome']