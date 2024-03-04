# 모듈 가져오기
import streamlit as st
import pprint
import requests
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import csv

# 데이터베이스 가져오기
cred = credentials.Certificate('bus-search-8aeac-firebase-adminsdk-3c2sn-510b8fe76b.json')

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
database = firestore.client()

def add_file():
    bus = database.collection('bus')
    file = open('프로젝트-버스정보/서울시버스정류소위치정보.csv', 'r', encoding='euc-kr')
    reader = csv.DictReader(file)

    batch = database.batch()  # 일괄 처리 객체 생성

    for index, row in enumerate(reader):
        data = {
            "NAME" : row['정류소명'],
            "STATION_ID" : row['정류소번호']
        }

        new_doc_ref = bus.document()  # 새로운 문서 참조 생성
        batch.set(new_doc_ref, data)  # 일괄 처리에 데이터 추가

        if (index + 1) % 500 == 0:  # 500개마다 일괄 처리 실행
            batch.commit()
            batch = database.batch()  # 새로운 일괄 처리 객체 생성
            print("500번 반복했습니다")

    # 마지막 일괄 처리 실행
    batch.commit()
    print('끝')

def take_bus(station_id):
    bus_info=[]
    service_key = 'Xhhtp6o3z4f7BOdsmlZ94BhZZKweTPbK9SwsaxHQmLhdWTYvOrFdAs4aSD6yPZZSJRh5VBGU2v+uABrSXp1bBQ=='
    url = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid'    
    
    params = {
        'ServiceKey' : service_key,
        'arsId' : station_id,
        'resultType' : 'json',
        # 'stId' : 111000213
    }
    response = requests.get(url, params=params)
    bus_info = []
    if response.status_code == 200:
        decoded_content = response.content.decode('utf-8')
        json_data = json.loads(decoded_content)
        bus_list = json_data['msgBody']['itemList']

        for b in bus_list:
            bus = {}
            if b['routeType'] == '3':
                bus['image'] = 'static/bus_blue@400.png'
            elif b['routeType'] == '2' or b['routeType'] == '4':
                bus['image'] = 'static/bus_green@400.png'
            elif b['routeType'] == '6':
                bus['image'] = 'static/bus_red@400.png'
            elif b['routeType'] == '5':
                bus['image'] = 'static/bus_yellow@400.png'
            else:
                bus['image'] = 'static/bus_gray@400.png'
            
            bus['bus_number1'] = b['busRouteAbrv']
            bus['arrive_time1'] = b['arrmsgSec1']
            bus['current_station1'] = b['stationNm1']
            bus['arrive_time2'] = b['arrmsgSec2']
            bus['current_station2'] = b['stationNm2']
            bus['station_name'] = b['stNm']

            # print(bus['arrive_time1'])
            if bus['arrive_time1'] == '첫 번째 버스 운행종료':
                pass
            elif bus['arrive_time2'] == None:
                pass
            else:
                bus_info.append(bus)

        return bus_info

def side_bar():
    # global bus_names
    with st.sidebar:
        
        # 데이터베이스 버스파일 bus_list에 저장하기
        if 'bus_list' not in st.session_state:
            st.session_state['bus_list'] = database.collection('bus').get()

        if 'bus_names' not in st.session_state:
            st.session_state['bus_names'] = []  # 1. 초기화
            for b in st.session_state['bus_list']:
                st.session_state['bus_names'].append([ b.to_dict()['NAME'], b.to_dict()['STATION_ID'] ])
            
        # 버스 검색하기
        search_name = st.text_input('Search the station ID')  
        search_names = []
        
        for bus_name in st.session_state['bus_names']:
            if search_name in bus_name[0]:
                search_names.append(bus_name)

        if search_name:
            if search_names:  # 검색 결과가 있을 때
                for p in search_names:
                    st.write("•  " + f"{p[0]}" + " :  " + f"**{p[1]}**")
            else:             # 검색 결과가 없을 때
                st.write("No matching results.")

def main():
    st.title(":blue[*Bus*] Information 🚌")
    side_bar()
    station_id = st.text_input('Type the station ID')

    try:
        # st.write('예시 ) 강동경희대병원: 25178, 고덕역: 25140, 강남역: 22298, 23285, 서울역: 11164')
        # st.divider()
        if station_id:
            bus_list = take_bus(station_id)
            st.subheader(f"{bus_list[0]['station_name']}({station_id})")
            st.divider()
            for bus in bus_list:
            # 두 개의 열 생성
                col1, col2 = st.columns([4, 5])  # 첫 번째 열은 이미지를 위해 1/5, 두 번째 열은 텍스트를 위해 4/5의 너비를 가짐

                # 첫 번째 열: 이미지
                with col1:
                    st.image(bus['image'], width=300)

                # 두 번째 열: 텍스트
                with col2:
                    st.write(f"버스 번호 : **{bus['bus_number1']}**")
                    if bus['current_station1'] == None:
                        pass
                    else:
                        st.write(f"현재 정류장 : **{bus['current_station1']}**")
                    st.write(f"도착 예정 시간 : **{bus['arrive_time1']}**")
                st.divider()
    except:
        st.write('정확하게 써주세요')

main()
# take_bus(25140)
# add_file()



    








