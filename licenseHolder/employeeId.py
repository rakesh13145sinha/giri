from .models import *

def employeeid_generate():
    try:
        latest_employee_id=Employee.objects.latest('employeeId')
        get_latest_employee_id=latest_employee_id.employeeId
        
        first_part_of_employee_id=get_latest_employee_id.split(".")[0]
        sec_part_of_employee_id=get_latest_employee_id.split(".")[1]
        
        new_employee_id=int(sec_part_of_employee_id)+1
       
        if len(str(new_employee_id))==2:
            
            return first_part_of_employee_id + "." + sec_part_of_employee_id[:3]+str(new_employee_id)
        
        elif len(str(new_employee_id))==3:
            
            return first_part_of_employee_id + "." + sec_part_of_employee_id[:2]+str(new_employee_id)
        
        elif len(str(new_employee_id))==4:
            
            return first_part_of_employee_id + "." + sec_part_of_employee_id[:1]+str(new_employee_id)
        
        elif len(str(new_employee_id))==5:
           
            return first_part_of_employee_id + "."+str(new_employee_id)
        else:
        
            return first_part_of_employee_id + "." +sec_part_of_employee_id[:4]+str(new_employee_id)
    
    except Exception as msg:
        return "EMP.00001"

def vendor_generate():
    try:
        latest_Vendor_id=Vendor.objects.latest('vendorId')
        get_latest_Vendor_id=latest_Vendor_id.vendorId
        
        first_part_of_Vendor_id=get_latest_Vendor_id.split(".")[0]
        sec_part_of_Vendor_id=get_latest_Vendor_id.split(".")[1]
        
        new_Vendor_id=int(sec_part_of_Vendor_id)+1
        print(new_Vendor_id)
        
        if len(str(new_Vendor_id))==2:
            
            return first_part_of_Vendor_id + "." + sec_part_of_Vendor_id[:3]+str(new_Vendor_id)
        
        elif len(str(new_Vendor_id))==3:
            
            return first_part_of_Vendor_id + "." + sec_part_of_Vendor_id[:2]+str(new_Vendor_id)
        
        elif len(str(new_Vendor_id))==4:
            
            return first_part_of_Vendor_id + "." + sec_part_of_Vendor_id[:1]+str(new_Vendor_id)
        
        elif len(str(new_Vendor_id))==5:
           
            return first_part_of_Vendor_id + "."+str(new_Vendor_id)
        else:
        
            return first_part_of_Vendor_id + "." +sec_part_of_Vendor_id[:4]+str(new_Vendor_id)
    
    except Exception as msg:
        return "VEN.00001"


def meterial_generate():
    try:
        latest_material_id=Material.objects.latest('materialId')
        get_latest_material_id=latest_material_id.materialId
        
        first_part_of_material_id=get_latest_material_id.split(".")[0]
        sec_part_of_material_id=get_latest_material_id.split(".")[1]
        
        new_material_id=int(sec_part_of_material_id)+1
       
        if len(str(new_material_id))==2:
            
            return first_part_of_material_id + "." + sec_part_of_material_id[:3]+str(new_material_id)
        
        elif len(str(new_material_id))==3:
            
            return first_part_of_material_id + "." + sec_part_of_material_id[:2]+str(new_material_id)
        
        elif len(str(new_material_id))==4:
            
            return first_part_of_material_id + "." + sec_part_of_material_id[:1]+str(new_material_id)
        
        elif len(str(new_material_id))==5:
           
            return first_part_of_material_id + "."+str(new_material_id)
        else:
        
            return first_part_of_material_id + "." +sec_part_of_material_id[:4]+str(new_material_id)
    
    except Exception as msg:
        return "MET.00001"




def project_generate():
    try:
        latest_project_id=Project.objects.latest('projectId')
        get_latest_project_id=latest_project_id.projectId
        
        first_part_of_project_id=get_latest_project_id.split(".")[0]
        sec_part_of_project_id=get_latest_project_id.split(".")[1]
        
        new_project_id=int(sec_part_of_project_id)+1
       
        if len(str(new_project_id))==2:
            
            return first_part_of_project_id + "." + sec_part_of_project_id[:3]+str(new_project_id)
        
        elif len(str(new_project_id))==3:
            
            return first_part_of_project_id + "." + sec_part_of_project_id[:2]+str(new_project_id)
        
        elif len(str(new_project_id))==4:
            
            return first_part_of_project_id + "." + sec_part_of_project_id[:1]+str(new_project_id)
        
        elif len(str(new_project_id))==5:
           
            return first_part_of_project_id + "."+str(new_project_id)
        else:
        
            return first_part_of_project_id + "." +sec_part_of_project_id[:4]+str(new_project_id)
    
    except Exception as msg:
        return "PRJ.00001"