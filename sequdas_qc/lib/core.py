import os
import subprocess
import argparse
import ConfigParser
import shutil
import sys
from validate_email import validate_email

from sequdas_qc.lib.sample_sheet import *
import sequdas_qc.conf

def run_parameter(argv):

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', "--in_dir", dest='inputfile', help="Input directory", required=True)
    parser.add_argument('-o', "--out_dir", dest='outfile', help="Output directory", required=True)
    parser.add_argument('-s', "--step", dest='step', help="step 1: Run MiSeq reporter\nstep 2: Run FastQC\nstep 3: Run MultiQC\nstep 4: Run Kraken\nstep 5: Run Kaiju\nstep 6: Run Kraken 2\nstep 7: Run IRIDA uploader", required=True)
    parser.add_argument('-C', "--config", dest='config_file_path', help="SeqUDAS config file", default=os.path.join(os.path.dirname(sequdas_qc.conf.__file__), "config.ini"))
    parser.add_argument('-u', "--sequdas_id", dest='sequdas_id', help="SeqUDAS ID", default="")
    parser.add_argument('-c', "--cluster", dest='cluster', help="Run analyses on HPC Cluster using DRMAA", default="False")
    parser.add_argument('-t', "--run_style", dest='run_style', action='store_true')
    parser.add_argument('-k', "--keep_kraken", dest='keep_kraken', help="Keep intermediate output files from kraken analysis", action='store_true')
    parser.add_argument('-x', "--keep_kaiju", dest='keep_kaiju', help="Keep intermediate output files from kaiju analysis", action='store_true')
    parser.add_argument('-n', "--run_uploader", dest='run_uploader', help="Run IRIDA uploader", action='store_true')
    parser.add_argument('-e', "--send_email", dest='send_email_switch', help="Send notification emails", action='store_true')
    args = parser.parse_args()

    return (
        args.inputfile,
        args.outfile,
        args.step,
        args.run_style,
        args.keep_kraken,
        args.keep_kaiju,
        args.run_uploader,
        args.sequdas_id,
        args.send_email_switch,
        args.cluster,
        args.config_file_path,
    )

def sequdas_config(config_file_path):
    try:
        config=read_config(config_file_path)
        confdict = {section: dict(config.items(section)) for section in config.sections()}
        return confdict
    except Exception as e :
        print(str(e),' Could not read configuration file')

def read_config(config_file_path):
    config = ConfigParser.RawConfigParser()
    try:
        config.read(config_file_path)
        return config
    except Exception as e :
        print(str(e))

def check_folder(foldername):
    if not os.path.exists(foldername):
        os.makedirs(foldername)
        return foldername

def copy_reporter(out_dir,run_folder_name):
    s_config=sequdas_config()
    ssh_host_report=s_config['reporter']['reporter_ssh_host']
    QC_img_dir=s_config['reporter']['qc_dir']
    print ssh_host_report
    print QC_img_dir
    rsynccmd = 'rsync -trvh --chmod=Du=rwx,Dog=rx,Fu=rwx,Fgo=rx -O '+ out_dir+"/"+run_folder_name +' '+ssh_host_report+':' + QC_img_dir
    rsyncproc = subprocess.call(rsynccmd,shell=True)
    return rsyncproc


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

def validate_email_address(email): 
    is_valid = validate_email(email)
    #match=re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*\.*[ca|com|org|edu]{3}$)",email)
    if is_valid:
        return 'Valid'
    else:
        return 'Invalid'

def check_path_with_slash(folder):
    if not folder.endswith("/"):
        folder += "/"
    return folder
    
def del_end_slash(folder):
    if folder.endswith("/"):
        folder=re.sub('/$', '', folder)
    return folder

def check_create_folder(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            print "make directory error, please check "+dirname
