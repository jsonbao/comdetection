#coding:UTF8
import MySQLdb
import time

class ClusterState(object):
    def __init__(self, uid=-1, workerid=-1):
        self.uid = uid
        self.workerid = workerid
        self.state = 0
        self.time = long(time.time())
        
class ClusterStateDao(object):
    def __init__(self, conn):
        self.conn = conn
    def open(self):
        pass
    
    def setupLease(self,state, preState):
        state.time=time.time()
        cursor = self.conn.cursor()
        count = 0
        
        try:
            if not preState:
                count = cursor.execute("insert into clusterstate(uid, state, time, workerid) values(%s, %d, %d);" % 
                               (state.uid, state.state, state.time, state.workerid))
            else:
                count = cursor.execute("update state = 0, time=%s, workerid=%s "\
                                       "where uid = %s and time = %s and workid=%s" % 
                                        (state.time, state.workerid,state.uid, preState.time, preState.workid))
        except Exception as ex:
            print str(ex)
            count = 0
        finally:
            cursor.close()
            self.conn.commit()
        
        return count > 0
                

    def extendLease(self, state):
        state.time=time.time()
        cursor = self.conn.cursor()
        count = 0
        try:
            count = cursor.execute("update state = %s, time=%s where uid = %s and workid=%s" % 
                                        (state.state, state.time, state.uid, state.workerid,))
        except Exception as ex:
            print str(ex)
        finally:
            cursor.close()
            self.conn.commit()
        if count > 0:
            return True
        else:
            return False
            
    def setClusterState(self, state):
        cursor = self.conn.cursor()
        try:
            cursor.execute("insert into clusterstate(uid, state, time, workerid) values(%s, %d, %d) "\
                           "on duplicate key update "\
                           "state=values(state),time=values(time), workerid=values(workerid);" % 
                           (state.uid, state.state, state.time, state.workerid))
        except Exception as ex:
            print str(ex)
        finally:
            cursor.close()
            self.conn.commit()
        
    def getClusterState(self, uid):
        cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("select * from clusterstate where uid='%s';" % (uid))
            rec = cursor.fetchone()
            
            ret = ClusterState()
            if rec:
                ret=(rec['state'], rec['time'])
                break
        except Exception as ex:
            print str(ex)
        
        finally:
            cursor.close()
            self.conn.commit()
        return ret
    
    def close(self):
        self.conn.close()