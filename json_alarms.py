import alarms
import pickle


alarms_data = [alarms.Alarm(),alarms.Alarm(atype=alarms.AlarmTypes.daily,alarm_time='10:00')]

with open('alarms.dat','wb') as f:
    pickle.dump(alarms_data,f)

del alarms_data[:]

with open('alarms.dat') as f:
    alarms_data = pickle.load(f)

print(alarms_data)