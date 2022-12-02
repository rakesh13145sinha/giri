from .models import Client,License

"""CLIENT ID AUTO GENERATE"""

def generate_client_id():
    try:
        latest_client=Client.objects.latest('create_date')
        get_latest_client_id=latest_client.client_id
        # print(get_latest_client_id)
        first_part_of_client_id=get_latest_client_id.split(".")[0]
        sec_part_of_client_id=get_latest_client_id.split(".")[1]
        # print(sec_part_of_client_id)
        new_client_id=int(sec_part_of_client_id)+1
        # print(new_client_id)
        if len(str(new_client_id))==2:
            
            return first_part_of_client_id + "." + sec_part_of_client_id[:3]+str(new_client_id)
        
        elif len(str(new_client_id))==3:
            
            return first_part_of_client_id + "." + sec_part_of_client_id[:2]+str(new_client_id)
        
        elif len(str(new_client_id))==4:
            
            return first_part_of_client_id + "." + sec_part_of_client_id[:1]+str(new_client_id)
        
        elif len(str(new_client_id))==5:
           
            return first_part_of_client_id + "."+str(new_client_id)
        else:
        
            return first_part_of_client_id + "." +sec_part_of_client_id[:4]+str(new_client_id)
    
    except Exception as msg:
        return "CLT.00001"

""""NUMBER OF LICENSE CREATE"""
def license_generate():
    try:
        latest_license_id=License.objects.latest('license_id')
        get_latest_license_id=latest_license_id.license_id
        # print(get_latest_license_id)
        first_part_of_license_id=get_latest_license_id.split(".")[0]
        sec_part_of_license_id=get_latest_license_id.split(".")[1]
        # print(sec_part_of_license_id)
        new_license_id=int(sec_part_of_license_id)+1
        # print(new_license_id)
        if len(str(new_license_id))==2:
            
            return first_part_of_license_id + "." + sec_part_of_license_id[:3]+str(new_license_id)
        
        elif len(str(new_license_id))==3:
            
            return first_part_of_license_id + "." + sec_part_of_license_id[:2]+str(new_license_id)
        
        elif len(str(new_license_id))==4:
            
            return first_part_of_license_id + "." + sec_part_of_license_id[:1]+str(new_license_id)
        
        elif len(str(new_license_id))==5:
           
            return first_part_of_license_id + "."+str(new_license_id)
        else:
        
            return first_part_of_license_id + "." +sec_part_of_license_id[:4]+str(new_license_id)
    
    except Exception as msg:
        return "LIC.00001"


