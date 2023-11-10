
import cx_Oracle as cx
import random as ra
import re
base = 100000

conn = cx.connect('scott', '1234', 'localhost:1521/xe')
cur = conn.cursor()
from collections import defaultdict,deque as que
history=que(maxlen=3)
dt=que(maxlen=12)
data_dict = {}
earn=[]
company_data_dict = defaultdict(lambda: que(maxlen=3))


def play():
    sw=True
    while sw:
        print('1. 가입하기')
        print('2.로그인')
        print('3. 나가기')
        a=int(input('선택 : '))
        if a==1:
            gaip()
        elif a==2:
            login()
        elif a==3:
            break
        else:
            print('다시해')
            return

def gaip():
    print('\n===회원가입=====')
    while True:
        userid=input('\n아이디를입력 q입력시 종료 : ')
        if userid=='q':
            break
        else:
            exp=re.findall('^[a-z0-9]{5,}',userid)
            if len(exp)==0:
                print('\n영소문자로 시작 숫자포함가능 5자이상 ')
                continue 
        pwd=input('\n비밀번호를입력 q입력시 종료: ')
        if pwd=='q':
            break
        else:
            exp=re.findall('^[a-z0-9]{8,}',pwd)
            if len(exp)==0:
                print('\n영소문자로 시작 숫자 포함가능 8자이상 ')
                continue      
        username=input('\n이름을입력 q입력시 종료 : ')
        if username=='q':
            break
        else:
            exp=re.findall('^[a-z]{5,}',username)
            if len(exp)==0:
                print('\n영소문자로 시작 5자이상 ')
                continue
        phone=input('\n번호를입력 q입력시 종료 : ')
        if phone=='q':
            break
        else:
            exp=re.findall('^[0-9]{3,}-[0-9]{4,}-[0-9]{4,}',phone)
            if len(exp)==0:
                print('\n넌 번호 형식도 모르니? xxx-xxxx-xxxx ')
                continue
            else:
                cur.execute('select * from member where  userid=:1 or pwd=:2',[userid,pwd])
                a=cur.fetchall()
                if len(a)==0:
                    cur.execute('insert into member values (:1,:2,:3,:4,0,1)',[userid,pwd,username,phone])
                    conn.commit()
                    print('\n가입 완료')
                    sw=False
                    break
                else:
                    print('\n이미 가입된 회원의 아이디 혹은 비밀번호')
            

def login():
    userid=input('\n아이디 입력 :')
    pwd=input('\n비번입력')
    cur.execute('select * from member where userid=:1 and pwd=:2',[userid,pwd])
    tet=cur.fetchone()
    if tet != None:
        main(tet)
    else:
        print('\n없는 아이디 혹은 비밀번호')
        return
            
def show_jusic():
    update()
    cur.execute('select * from jusic')
    data = cur.fetchall()
    print('\n================주식 목록====================')
    print('%-3s\t%-15s\t%-6s'%('코드','이름','가격'))
    for row in data:
        print('%-3d\t%-15s\t%-6d'%(row[0],row[1],row[2]))
                   
def my_jusic():
    global earn
    global base
    tot=0
    cur.execute('select * from myjusic where cnt !=0 order by code ')
    earn=cur.fetchall()
    update()
    cur.execute('select code, money from jusic')      
    data=cur.fetchall()
    for code,money in data:
        cur.execute('update myjusic set money = :1 where code = :2', [money, code])
        conn.commit()            
    cur.execute('select * from myjusic where cnt !=0 order by code ')
    dat = cur.fetchall()
    print('\n================내 주식=====================')
    print('%-3s\t%-15s\t%-6s%-3s\t%-3s'%('코드','이름','가격','수량','수익률'))
  
 #for row in dat:
 #       print('%-3d\t%-15s\t%-6d\t%-3s'%(row[4],row[1],row[2],row[3]))

    for i in range(len(dat)):
        print('%-3d\t%-15s\t%-6d\t%-3s\t%0.2f%%'%(dat[i][4],dat[i][1],dat[i][2],dat[i][3],((dat[i][2]-earn[i][2])/earn[i][2])*100))
        tot+=dat[i][2]

    print(f'『자본금』 = 【{base}】')
    print(f'『내 주식의 총합』 = 【{tot}】')
    

        

def update():
    cur.execute('select code, money from jusic')
    data =cur.fetchall()   
    for code, money in data:
        change = ra.randrange(-1000, 3000, 1000)
        new_money = money + change
        cur.execute('update jusic set money = :1 where code = :2', [new_money, code])
        conn.commit()  
        
def histo():
    update()
    global dt
    global data_dict
    cur.execute('select code,name, money from jusic')
    data =cur.fetchall()   
    history.append(data)
    print('\n================주식 목록====================')
    print('%-3s\t%-15s\t%-6s'%('코드','이름','가격'))
    for i in range(len(history)):
        for j in range(len(history[i])): 
            dt.append(history[i][j])   
   # for i in range(len(history)):
       #  for j in range(len(history[i])): 
        #     print('%-3d\t%-15s\t%-6d'%(history[i][j]))
         #    print('============')
    for entry in data:
        identifier, company_name, stock_price = entry
        company_data = company_data_dict[company_name]
        company_data.append((identifier, stock_price))
        company_data_dict[company_name] = company_data  # 중요: 데이터 갱신

# 결과 출력
    for company_name, company_data in company_data_dict.items():
        print(f"Company: {company_name}")
        for identifier, stock_price in company_data:
            print(f"Period {identifier}: {stock_price}")
        print("=" * 40)
            
            
def sell():
    global base
    y=[]
    sells=0
    check = True
    while check:
        my_jusic()
        cur.execute('select code from jusic')
        lists=cur.fetchall()
        for i in lists:
            y.append(i[0])          
        code=int(input(' 팔 주식의 번호를 입력 0이면 취소:'))
        if code==0:
            check = False
            continue
        elif code not in y:
            print('없는 코드입니다')
            continue
        else:                                
            cnt=int(input('팔 개수를 선택 0이면 취소 :'))
            cur.execute('select code from jusic')
            lists=cur.fetchall()
            cur.execute('select cnt from myjusic where code=:1',[code])
            hm=cur.fetchone()
            if cnt==0:
                break
            elif cnt>hm[0]:
                print('팔려는 개수가 가진 것보다 많음')
                continue
            else:          
                cur.execute('select money from jusic where code=:1',[code])
                money=cur.fetchall()
                k=hm[0]-cnt
                print()
                print('판 금액: ',money[0][0])
                print()
                sells += int(cnt) * money[0][0]
                base+=sells              
                cur.execute('update myjusic set cnt=:1 where code=:2',[k,code])
                conn.commit()    
                    
def menu():
    print('\n========주식 프로그램=======')
    print('1.주식목록 \n2.내 주식\n3.주식 구매 \n4.주식 판매 \n5.종료 \n6.증감기록')
          
        
#def earn():
   # cur.execute('select * from jusic')
   # earn=cur.fetchall()
    #for i in earn:
        #print(i)
    
    
    
    
 #실행파일
def main(tot):
    print()
    print(f'{tot[2]}님 환영합니다 도전횟수={tot[5]} 성공횟수 = {tot[4]}')
    cur.execute('select clear,try from member where userid=:1',[tot[0]])
    lits=cur.fetchall()
    clear=lits[0][0]
    trys=lits[0][1]
    global base
    ck=True
    while ck:
        if base>200000:
            print('승리')
            clear+=1
            trys+=1
            cur.execute('update member set clear=:1, try=:2 where userid=:3',[clear,trys,tot[0]])  
            conn.commit()
            ck=False
        elif base<0:
            print('파산')
            trys+=1
            cur.execute('update member set try=:1 where userid=:2',[trys,tot[0]])
            conn.commit()
            ck=False
        else:
            menu()
            print(f'『자본금』 = 【{base}】')
            ch=int(input('menu :'))
            if ch==1:
                show_jusic()
            elif ch==2:
                my_jusic()
            elif ch==3:
                buy()
            elif ch==4:
                sell()            
            elif ch==5:
                print('종료')
                trys+=1
                cur.execute('update member set try=:1 where userid=:2',[trys,tot[0]])
                conn.commit()
                ck=False
            elif ch==6:
                histo()  
            else:
                print('잘못된 선택')
            
def buy():
    global base
    y=[]
    sells=0
    check = True
    while check:
        show_jusic()
        cur.execute('select code from jusic')
        lists=cur.fetchall()
        for i in lists:
            y.append(i[0])          
        code=int(input(' 살 주식의 번호를 입력 0이면 취소:'))
        if code==0:
            check = False
            continue
        elif code not in y:
            print('없는 코드입니다')
            continue
        else:                                
            cnt=int(input('살 개수를 선택 :'))
            if cnt==0:
                break
            else:          
                cur.execute('select code,name,money from jusic where code=:1',[code])
                lists=cur.fetchall()
                cur.execute('select * from myjusic where code=:1',[code])
                lst=len(cur.fetchall())
              
                if lst==0:
                    cur.execute('select money from jusic where code=:1',[code])
                    money=cur.fetchone()[0]
                    if (money*cnt)>base:
                        print('돈이 부족합니다')
                        continue
                    else:
                        cur.execute('insert into myjusic values(mseq.nextval,:1,:2,:3,:4)',[lists[0][1],lists[0][2],cnt,lists[0][0]])
                        base-=int(cnt)*lists[0][2]
                else:
                    cur.execute('select money from myjusic where code=:1',[code])
                    money=cur.fetchone()[0]
                    if (money*cnt)>base:
                        print('돈이 부족합니다')
                        continue
                    else:
                        cur.execute('select cnt from myjusic where code=:1',[code])
                        before=cur.fetchone()[0]
                        print(before)
                        before+=cnt 
                        cur.execute('update myjusic set cnt=:1 where code=:2',[before,code])
                        base-=int(cnt)*money
               
                my_jusic()       
                conn.commit()    
          

       
#진입점
if __name__ == '__main__':
    play()
  