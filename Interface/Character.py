class Character_split:
    def split_Four(self,Four):
        s1_list = str(Four).split('.')
        s1_new = s1_list[0] + '.' + s1_list[1][:4]
        return s1_new.rstrip('0').strip('.')
    def split_to(self,to):
        s1_list = str(to).split('.')
        s1_new = s1_list[0] + '.' + s1_list[1][:2]

        return s1_new.rstrip('0').strip('.')
    def split_rstrip(self,rs_strip):
        return str(rs_strip).rstrip('0').strip('.')
