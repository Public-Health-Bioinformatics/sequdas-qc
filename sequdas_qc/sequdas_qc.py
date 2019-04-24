#!/usr/bin/env python
######################################################################
#								     #
# BCCDC MiSEQ Archiving System (Sequdas)                             #
#	                                 			     #
#								     #
#								     #
# Jun Duan                                                           #
# BCCDC Public Health Laboratory                                     #
# University of British Columbia                                     #
# jun.duan@bccdc.ca                                                  #
#                                                                    #
# William Hsiao, PhD                                                 #
# Senior Scientist (Bioinformatics), BCCDC Public Health Laboratory  #
# Clinical Assistant Professor, Pathology & Laboratory Medicine, UBC #
# Adjunct Professor, Molecular Biology and Biochemistry, SFU         #
# Rm 2067a, 655 West 12th Avenue                                     #
# Vancouver, BC, V5Z 4R4                                             #
# Canada                                                             #
# Tel: 604-707-2561                                                  #
# Fax: 604-707-2603                                                  #
######################################################################

import sys
import re
import shutil
import logging
from .lib.core import *
from .lib.status_log import *
from .lib.sample_sheet import *
from .lib.pipe import *
from .lib.status_db import *
from .lib.message import *
import json

# S1: MiSeq reporter 4
# S2: FastQC 5 
# S3: MultiQC 6 
# S4: Kraken 7
# S5: IRIDA uploader 8
                        

def main(argv = None):
    if argv is None:
        argv = sys.argv
    (input_dir, out_dir,step_id,run_style,keep_kraken,keep_kaiju,run_uploader,sequdas_id,send_email_switch, cluster, config_file_path)=run_parameter(argv)
    run_name=os.path.basename(os.path.normpath(input_dir))
    run_analysis_folder=out_dir+"/"+run_name
    check_folder(out_dir)
    check_folder(run_analysis_folder)
    s_config=sequdas_config(config_file_path)
    logfile_dir=s_config['basic']['logfile_dir']
    logfile_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),s_config['basic']['logfile_dir'])
    logfile_dir=check_path_with_slash(logfile_dir)
    check_create_folder(logfile_dir)
    logfile=logfile_dir+"sequdas_server_log.txt"
    logfile_details_file=logfile_dir+"sequdas_server_details_log.txt"
    log_details=s_config['basic']['write_logfile_details']
    log_details=str2bool(log_details)
    # Email setting
    gmail_user= s_config['email_account']['gmail_user']
    gmail_pass= s_config['email_account']['gmail_pass']
    admin_emails= s_config['basic']['admin_email']
    split_pattern = re.compile(r"[;,]")
    email_list_admin=split_pattern.split(admin_emails)
    email_list=email_list_admin
    server_dir = s_config['basic']['server_dir']
    db = s_config['kraken']['db']
    irida = s_config['uploader']['irida']
    db_config = {
        'passwd': s_config['mysql_account']['mysql_passwd'],
        'host': s_config['mysql_account']['mysql_host'],
        'user': s_config['mysql_account']['mysql_user'],
        'db': s_config['mysql_account']['mysql_db'],
    }
    if send_email_switch is True:
        sample_sheets=[input_dir+"/"+"SampleSheet.csv"]
        metadata=parse_metadata(sample_sheets[0])
        investigator_list = split_pattern.split(metadata["investigatorName"])
        for operator in investigator_list:
            operator.replace(" ","")
            if(validate_email_address(operator).lower()=="valid"):
                email_list.append(operator)
    if log_details is True:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logfile_details_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s() - %(levelname)s - %(message)s',"%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if log_details is True:	 	
        logger.info("##############################################\n\nStart analyzing for "+run_name+"\n")
    add_status_starting(logfile,run_name,input_dir)        
    step_id=int(step_id)
    status_on_db=""
    #################################
    if(step_id==1):
        try:
            run_machine_QC(input_dir,out_dir)
            filter_sheet(input_dir,out_dir)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1): 	
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(db_config, sequdas_id,step_id,status)
        if run_style is True:
            step_id=step_id+1
        filter_sheet(input_dir,out_dir)
    if(step_id==2):
        if cluster == True:
            try:
                run_fastqc_cluster(input_dir,out_dir,server_dir)
                copy_reporter(out_dir,run_name)
                status=1
            except:
                status=0
        if cluster == False:
            try:
                run_fastqc(input_dir,out_dir,server_dir)
                copy_reporter(out_dir,run_name)
                status=1
            except:
                status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)
        if run_style is True:
            step_id=step_id+1
    if(step_id==3):
        try:
            run_multiQC(input_dir,out_dir)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)  
        if run_style is True:
            step_id=step_id+1         
    if(step_id==4):
        try:
            run_kraken(input_dir,out_dir,keep_kraken)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)            
        if run_style is True:
            step_id=step_id+1
    if(step_id==5):
        try:
            run_kaiju(input_dir,out_dir,keep_kraken)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)            
        if run_style is True:
            step_id=step_id+1
    if(step_id==6):
        if cluster == True:
            try:
                run_kraken2_cluster(input_dir,out_dir,keep_kraken,db,server_dir)
                copy_reporter(out_dir,run_name)
                status=1
            except:
                status=0
        if cluster == False:
            try:
                run_kraken2(input_dir,out_dir,keep_kraken, db, server_dir)
                copy_reporter(out_dir,run_name)
                status=1
            except:
                status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)            
        if run_style is True:
            step_id=step_id+1
    if(step_id==7 and run_uploader is True):
        try:
            filter_sheet(input_dir,out_dir)
            Upload_to_Irida(input_dir, irida)
            status=1
        except:
            status=0
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)
    if send_email_switch is True:
        send_email(gmail_user,gmail_pass,email_list,"Analysis is finished",run_name,"")                
    logger.info("############################################## End"+"\n")
if __name__ == "__main__":
    main(sys.argv[1:])
