import MySQLdb
import time
from sequdas_qc.lib.core import *


def doInsert(db_config, bccdc_id_value,source_value,fullpath_value,folder_value,analysis_status,start_time_value,sample_infor) :
    myConnection = MySQLdb.connect( host=db_config['host'], user=db_config['user'], passwd=db_config['passwd'], db=db_config['db'])
    cur = myConnection.cursor()
    end_time_value=""
    cur.execute("INSERT INTO status_table (bccdc_id,source,fullpath,folder,status,start_time,end_time,sample) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(bccdc_id_value,source_value,fullpath_value,folder_value,analysis_status,start_time_value,end_time_value,sample_infor))
    myConnection.commit()
    myConnection.close()

def update_from_server(db_config, sequdas_id,analysis_status,step):
    myConnection = MySQLdb.connect( host=db_config['host'], user=db_config['user'], passwd=db_config['passwd'], db=db_config['db'])
    timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
    cur = myConnection.cursor()
    cur.execute(("UPDATE status_table SET analysis_status=%s,end_time=%s,status=%s WHERE bccdc_id=%s"),(analysis_status,timestamp,step,sequdas_id))
#    #cur.execute(("UPDATE status_table SET analysis_status=%s,end_time=%s,status=%s WHERE bccdc_id=%s"),(analysis_status,timestamp,step,sequdas_id))
    myConnection.commit()
    myConnection.close()

def status_update(db_config, sequdas_id,step_id,status):
    step_name="s"+str(step_id)
    step=int(step_id)+3
    if(len(get_status(sequdas_id))>0):
        json_acceptable_string = get_status(sequdas_id).replace("'", "\"")
        status_on_db = json.loads(get_status(sequdas_id))
    else:
        status_on_db = {}
    status_on_db[step_name]=str(status)
    status_on_db_str=json.dumps(status_on_db)
    print sequdas_id
    print status_on_db_str
    print step
    update_from_server(db_config, sequdas_id,status_on_db_str,step)

def get_status(db_config, sequdas_id):
    myConnection = MySQLdb.connect( host=db_config['host'], user=db_config['user'], passwd=db_config['passwd'], db=db_config['db'])
    cur = myConnection.cursor()
    cur.execute(("SELECT analysis_status FROM `status_table` WHERE bccdc_id=%s order by id desc LIMIT 1"),(sequdas_id,))    
    data = cur.fetchone()
    cur.close()
    #print data[0]
    if(data):
        return data[0]
    else:
        status={}
        return status
