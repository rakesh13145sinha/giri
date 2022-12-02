from .models import *
def qualitycheacklist():
    try:
        latest_quality_id=QualityCheckList.objects.latest('qualityid')
        get_latest_quality_id=latest_quality_id.qualityid
        
        first_part_of_quality_id=get_latest_quality_id.split(".")[0]
        sec_part_of_quality_id=get_latest_quality_id.split(".")[1]
        
        new_quality_id=int(sec_part_of_quality_id)+1
       
        if len(str(new_quality_id))==2:
            
            return first_part_of_quality_id + "." + sec_part_of_quality_id[:3]+str(new_quality_id)
        
        elif len(str(new_quality_id))==3:
            
            return first_part_of_quality_id + "." + sec_part_of_quality_id[:2]+str(new_quality_id)
        
        elif len(str(new_quality_id))==4:
            
            return first_part_of_quality_id + "." + sec_part_of_quality_id[:1]+str(new_quality_id)
        
        elif len(str(new_quality_id))==5:
           
            return first_part_of_quality_id + "."+str(new_quality_id)
        else:
        
            return first_part_of_quality_id + "." +sec_part_of_quality_id[:4]+str(new_quality_id)
    
    except Exception as msg:
        return "QLT.00001"

def seftycheacklist():
    try:
        latest_sefty_id=SeftyCheckList.objects.latest('saftychecklistid')
        get_latest_sefty_id=latest_sefty_id.saftychecklistid
        
        first_part_of_sefty_id=get_latest_sefty_id.split(".")[0]
        sec_part_of_sefty_id=get_latest_sefty_id.split(".")[1]
        
        new_sefty_id=int(sec_part_of_sefty_id)+1
       
        if len(str(new_sefty_id))==2:
            
            return first_part_of_sefty_id + "." + sec_part_of_sefty_id[:3]+str(new_sefty_id)
        
        elif len(str(new_sefty_id))==3:
            
            return first_part_of_sefty_id + "." + sec_part_of_sefty_id[:2]+str(new_sefty_id)
        
        elif len(str(new_sefty_id))==4:
            
            return first_part_of_sefty_id + "." + sec_part_of_sefty_id[:1]+str(new_sefty_id)
        
        elif len(str(new_sefty_id))==5:
           
            return first_part_of_sefty_id + "."+str(new_sefty_id)
        else:
        
            return first_part_of_sefty_id + "." +sec_part_of_sefty_id[:4]+str(new_sefty_id)
    
    except Exception as msg:
        return "HSE.00001"

def qualityquestionid():
    try:
        latest_qlyquestion_id=QualityQuestion.objects.latest('questionid')
        get_latest_qlyquestion_id=latest_qlyquestion_id.questionid
        
        first_part_of_qlyquestion_id=get_latest_qlyquestion_id.split(".")[0]
        sec_part_of_qlyquestion_id=get_latest_qlyquestion_id.split(".")[1]
        
        new_qlyquestion_id=int(sec_part_of_qlyquestion_id)+1
       
        if len(str(new_qlyquestion_id))==2:
            
            return first_part_of_qlyquestion_id + "." + sec_part_of_qlyquestion_id[:3]+str(new_qlyquestion_id)
        
        elif len(str(new_qlyquestion_id))==3:
            
            return first_part_of_qlyquestion_id + "." + sec_part_of_qlyquestion_id[:2]+str(new_qlyquestion_id)
        
        elif len(str(new_qlyquestion_id))==4:
            
            return first_part_of_qlyquestion_id + "." + sec_part_of_qlyquestion_id[:1]+str(new_qlyquestion_id)
        
        elif len(str(new_qlyquestion_id))==5:
           
            return first_part_of_qlyquestion_id + "."+str(new_qlyquestion_id)
        else:
        
            return first_part_of_qlyquestion_id + "." +sec_part_of_qlyquestion_id[:4]+str(new_qlyquestion_id)
    
    except Exception as msg:
        return "QLQ.00001"


def seftyquestionid():
    try:
        latest_seftyquestion_id=SeftyQuestion.objects.latest('questionid')
        get_latest_seftyquestion_id=latest_seftyquestion_id.questionid
        
        first_part_of_seftyquestion_id=get_latest_seftyquestion_id.split(".")[0]
        sec_part_of_seftyquestion_id=get_latest_seftyquestion_id.split(".")[1]
        
        new_seftyquestion_id=int(sec_part_of_seftyquestion_id)+1
       
        if len(str(new_seftyquestion_id))==2:
            
            return first_part_of_seftyquestion_id + "." + sec_part_of_seftyquestion_id[:3]+str(new_seftyquestion_id)
        
        elif len(str(new_seftyquestion_id))==3:
            
            return first_part_of_seftyquestion_id + "." + sec_part_of_seftyquestion_id[:2]+str(new_seftyquestion_id)
        
        elif len(str(new_seftyquestion_id))==4:
            
            return first_part_of_seftyquestion_id + "." + sec_part_of_seftyquestion_id[:1]+str(new_seftyquestion_id)
        
        elif len(str(new_seftyquestion_id))==5:
           
            return first_part_of_seftyquestion_id + "."+str(new_seftyquestion_id)
        else:
        
            return first_part_of_seftyquestion_id + "." +sec_part_of_seftyquestion_id[:4]+str(new_seftyquestion_id)
    
    except Exception as msg:
        return "HSQ.00001"