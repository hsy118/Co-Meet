from django.shortcuts import render
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.http.response import JsonResponse
from api.models import Fpopl, CoronaData, Gugun, Fpopl_BC
from user.models import SearchLog
from recomm.models import CoronaWeight, DistanceData, DistWeight, FpoplWeight
from user.serializers import SearchSerializer, SearchLogSerializer, SearchBodySerializer, SearchLogBodySerializer
from drf_yasg.utils import swagger_auto_schema
import pandas as pd
from datetime import datetime, timedelta, date
from collections import Counter
import math

class SaveDistWeight(viewsets.GenericViewSet, mixins.ListModelMixin, View):

    def save_dist_list(self, *args, **kwargs):

        # 각 구의 리스트를 DB에서 조회
        gugun_list = Gugun.objects.all()

        for i in gugun_list.values("signgu_nm"):
            signgu_nm = i["signgu_nm"]
            near_area = nearbyArea(signgu_nm)
            nm = []

            for idx, j in enumerate(near_area):
                nm.append({'signgu_nm': j[0], 'weight_point': j[1]})
            dist_weight = DistanceData(
                signgu_nm=signgu_nm, dist_weights=nm)
            dist_weight.save()

        return Response(status=200)

class SaveCoronaWeight(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    def save_corona_weight(self, *args, **kwargs):
        today = datetime.today()
        recentdate = datetime(2021, 3, 31, 0, 0, 0)
        cal = recentdate - datetime(2021, recentdate.month - 2, 1, 0, 0, 0)
        standard = recentdate - timedelta(cal.days)
        corona = CoronaData.objects.filter(
            date__range=[standard.strftime('%Y-%m-%d'), recentdate.strftime('%Y-%m-%d')])
        df = pd.DataFrame(
            list(corona.values('date', 'gugun', 'serial_number')))

        df['date'] = [''.join(x.split('-')[0:2])
                      for x in df.date]  # 2020-01 2020-01 2021-03-07 -> 202001, 202103
        df = df.groupby(["gugun", "date"], as_index=False).count()
        df = df.set_index('gugun')
        df = df.drop(index='기타', axis=0)
        df = df.drop(index='타시도', axis=0)
        df = df.rename_axis('gugun').reset_index()

        # 구 별로 월 별 코로나 평균
        df_first = df[df["date"] == "202101"].groupby(by=["date"]).sum()
        df_second = df[df["date"] == "202102"].groupby(by=["date"]).sum()
        df_third = df[df["date"] == "202103"].groupby(by=["date"]).sum()

        first_avg = df_first.iloc[0]['serial_number'] / 25
        second_avg = df_second.iloc[0]['serial_number'] / 25
        third_avg = df_third.iloc[0]['serial_number'] / 25

        df_first = df[df["date"] == "202101"]
        df_first["serial_number"] = [
            x/first_avg for x in df_first.serial_number]
        df_second = df[df["date"] == "202102"]
        df_second["serial_number"] = [
            x/second_avg for x in df_second.serial_number]
        df_third = df[df["date"] == "202103"]
        df_third["serial_number"] = [
            x/third_avg for x in df_third.serial_number]
        first_list = df_first.sort_values(by=['serial_number'], axis=0)
        second_list = df_second.sort_values(by=['serial_number'], axis=0)
        third_list = df_third.sort_values(by=['serial_number'], axis=0)

        temp_list = pd.concat([first_list, second_list, third_list])
        list_1 = first_list['gugun'].to_list()
        list_2 = second_list['gugun'].to_list()
        list_3 = third_list['gugun'].to_list()

        weight_1 = {string: (i + 1) for i, string in enumerate(list_1)}
        weight_2 = {string: (i + 1) for i, string in enumerate(list_2)}
        weight_3 = {string: (i + 1) for i, string in enumerate(list_3)}

        total_corona_rate = Counter(
            weight_1) + Counter(weight_2) + Counter(weight_3)

        gugun_list = list(Gugun.objects.values())

        # 기존 코로나 데이터 삭제
        corona_weight_data = CoronaWeight.objects.all()
        for i in range(0, corona_weight_data.count()):
            corona_weight_data[0].delete()

        data = {'gugun': [], 'before_corona_rate': [],
                'after_corona_rate': [], 'serial_number': []}
        corona_df = pd.DataFrame(data)
        for i in range(0, len(gugun_list)):
            temp_df = df[df['gugun'] == gugun_list[i]['signgu_nm']]
            cor1 = temp_df.iloc[0]['serial_number']
            cor2 = temp_df.iloc[1]['serial_number']
            cor3 = temp_df.iloc[2]['serial_number']
            # 1~2월 코로나 확진자 변화율
            temp_df['before_corona_rate'] = ((cor2 - cor1) / cor1) * 100
            # 2~3월 코로나 확진자 변화율
            temp_df['after_corona_rate'] = ((cor3 - cor2) / cor2) * 100
            temp_df = temp_df.groupby(["gugun"], as_index=False).mean()
            corona_df = corona_df.append(temp_df, ignore_index=False)

        before_corona_list = corona_df.sort_values(
            by=['before_corona_rate'], axis=0)
        after_corona_list = corona_df.sort_values(
            by=['after_corona_rate'], axis=0)

        before_list = before_corona_list['gugun'].to_list()
        after_list = after_corona_list['gugun'].to_list()

        before_1 = {string: (i + 1) for i,
                    string in enumerate(before_list)}
        after_2 = {string: (i + 1) for i,
                   string in enumerate(after_list)}

        total_corona_rate = total_corona_rate + \
            Counter(before_1) + Counter(after_2)

        # 구군 이름, 1~2월 변화량, 2~3월 변화량
        for signgu_nm, point in total_corona_rate.items():
            coronaWeight = CoronaWeight(
                signgu_nm=signgu_nm, weight_point=point)
            # 계산을 해서 저장
            coronaWeight.save()

        return HttpResponse(status=status.HTTP_200_OK)

class SaveFpoplWeight(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    def save_fpopl_weight(self, *args, **kwargs):
        today = datetime.today()

        cal = today - datetime(2020, 12, 1, 0, 0, 0)
        standard = today - timedelta(cal.days)
        fpopl_list = Fpopl.objects.filter(
            date__range=[standard.strftime('%Y%m%d'), today.strftime('%Y%m%d')]
        )
        df = pd.DataFrame(list(fpopl_list.values("date", "popl", "gugun")))

        # 2020-01 2020-01 2021-03-07 -> 202001, 202103
        df['date'] = [x[0:6] for x in df.date]
        df = df.groupby(by=["gugun", "date"], as_index=False).sum()

        # 월별 총 유동인구수
        df_first = df[df['date'] == '202012'].groupby(by=['date']).sum()
        df_second = df[df['date'] == '202101'].groupby(by=['date']).sum()
        df_third = df[df['date'] == '202102'].groupby(by=['date']).sum()

        a = df_first.iloc[0]['popl']
        b = df_second.iloc[0]['popl']
        c = df_third.iloc[0]['popl']

        # 상대적 유동인구 분포율
        relative_first = df[df['date'] == '202012']
        relative_first['popl'] = [(x/a)*100 for x in relative_first.popl]
        relative_second = df[df['date'] == '202101']
        relative_second['popl'] = [(x/b)*100 for x in relative_second.popl]
        relative_third = df[df['date'] == '202102']
        relative_third['popl'] = [(x/c)*100 for x in relative_third.popl]

        # 유동인구수 평균 - 25개 구
        a = df_first.iloc[0]['popl'] / 25
        b = df_second.iloc[0]['popl'] / 25
        c = df_third.iloc[0]['popl'] / 25

        # 유동인구수 - 평균 유동인구수보다 유동인구수가 많은 지역을 1로 적은 지역은 0으로 표시
        absolute_first = df[df['date'] == '202012']
        absolute_first['popl'] = [1 if x - a >
                                  0 else 0 for x in absolute_first.popl]
        absolute_second = df[df['date'] == '202101']
        absolute_second['popl'] = [1 if x - b >
                                   0 else 0 for x in absolute_second.popl]
        absolute_third = df[df['date'] == '202102']
        absolute_third['popl'] = [1 if x - c >
                                  0 else 0 for x in absolute_third.popl]

        # 유동인구 변화량 계산
        gugun_list = list(Gugun.objects.values())

        data = {'gugun': [], 'popl': [],
                'first_popl_rate': [], 'second_popl_rate': []}
        fpop_rate = pd.DataFrame(data)
        for i in range(0, len(gugun_list)):
            temp_df = df[df['gugun'] == gugun_list[i]['signgu_nm']]
            popl_first = temp_df.iloc[0]['popl']
            popl_second = temp_df.iloc[1]['popl']
            popl_third = temp_df.iloc[2]['popl']
            # 12~1월 유동인구 변화율
            temp_df['first_popl_rate'] = (
                (popl_second - popl_first) / popl_first) * 100
            # 1~2월 유동인구 변화율
            temp_df['second_popl_rate'] = (
                (popl_third - popl_second) / popl_second) * 100
            temp_df = temp_df.groupby(["gugun"], as_index=False).mean()

            fpop_rate = fpop_rate.append(temp_df, ignore_index=False)

        # 해당 구의 유동인구 / 전체 유동인구 => 등수
        point_1 = relative_third.sort_values(by=['popl'], axis=0)
        list_1 = point_1['gugun'].to_list()
        weight_1 = {string: (i + 1) * 3 for i, string in enumerate(list_1)}

        # 첫번째 달에서 두번째 달 넘어가는 걸로 소트해서 등수(12 => 1)
        point_2 = fpop_rate.sort_values(by=['first_popl_rate'], axis=0)
        list_2 = point_2['gugun'].to_list()
        weight_2 = {string: (i + 1) * 2 for i, string in enumerate(list_2)}

        # 두번째 달 넘어가는 거에서 세번째 달 넘어가는 걸로 소트해서 등수(1 => 2)
        point_3 = fpop_rate.sort_values(by=['second_popl_rate'], axis=0)
        list_3 = point_3['gugun'].to_list()
        weight_3 = {string: (i + 1) * 3 for i, string in enumerate(list_3)}

        total_score = Counter(weight_1) + Counter(weight_2) + Counter(weight_3)

        # 기존  데이터 삭제
        fpopl_weight_data = FpoplWeight.objects.all()
        for i in range(0, fpopl_weight_data.count()):
            fpopl_weight_data[0].delete()

        # 데이터 새로 저장
        for gugun, point in total_score.items():
            fpopl_weight = FpoplWeight(
                signgu_nm=gugun, weight_point=point)
            # 계산을 해서 저장
            fpopl_weight.save()

        return Response(status=200)

class RecommendPlace(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = SearchLogSerializer

    @swagger_auto_schema(request_body=SearchLogBodySerializer)
    def recommend(self, request):
        data = request.data
        gugun_list = Gugun.objects.all()
        corona_weight = CoronaWeight.objects.all()
        fpopl_weight = FpoplWeight.objects.all()
        dist_weight = DistanceData.objects.filter(
            signgu_nm=midpoint(request.data["searchList"])).values('dist_weights')

        dist_weight = list(
            list(dist_weight.values('dist_weights'))[0].values())
        dist_weight = dist_weight[0]
        # 구군 리스트를 가져와 디비에서 (25개 구)
        # 이걸 포문을 돌려요
        # for 문 안에서 구군이름으로 필터를 돌려서 점수들을 뽑은다음에
        # 가중치 적용해서 점수를 새로 뽑아요 그리고 그걸 한 리스트에 넣어요
        # 정렬해요
        # 상위에서 3개 뽑아요
        # 끝

        new_point = []

        for i in range(0, len(gugun_list)):
            gugun_name = gugun_list[i].signgu_nm
            corona_weight_point = list(corona_weight.filter(
                signgu_nm=gugun_name).values("weight_point"))[0]['weight_point']
            fpopl_weight_point = list(fpopl_weight.filter(
                signgu_nm=gugun_name).values("weight_point"))[0]['weight_point']
            dist_weight_point = [
                x for x in dist_weight if x['signgu_nm'] == gugun_name][0]['weight_point']

            sum_point = corona_weight_point + fpopl_weight_point + dist_weight_point

            new_point.append({'signgu_nm': gugun_name, 'point': sum_point})

        new_point.sort(key=lambda x: x["point"])

        df = pd.DataFrame(data=new_point)

        df_json = df.to_dict()

        ltln_dic = {"signgu_nm": [], "lat": [], "lng": []}
        total_dic = []
        for i in new_point:
            filter_list = gugun_list.filter(signgu_nm=i["signgu_nm"])

            for j in filter_list.iterator():
                lat = j.lat
                lng = j.lng

                ltln_dic["signgu_nm"].append(j.signgu_nm)
                ltln_dic["lat"].append(j.lat)
                ltln_dic["lng"].append(j.lng)

            target_corona_data = CoronaData.objects.filter(
                gugun=i["signgu_nm"]).exclude(discharge="퇴원")
            # 월별로 정렬
            df = pd.DataFrame(list(target_corona_data.values("gugun", "date")))
            # 먼저 일별로 정리
            df = df.groupby(by=["date"], as_index=False).count()
            # 월별로 통합
            df_2003 = df[df["date"].str.contains("2020-03")]
            df_2004 = df[df["date"].str.contains("2020-04")]
            df_2005 = df[df["date"].str.contains("2020-05")]
            df_2006 = df[df["date"].str.contains("2020-06")]
            df_2007 = df[df["date"].str.contains("2020-07")]
            df_2008 = df[df["date"].str.contains("2020-08")]
            df_2009 = df[df["date"].str.contains("2020-09")]
            df_2010 = df[df["date"].str.contains("2020-10")]
            df_2011 = df[df["date"].str.contains("2020-11")]
            df_2012 = df[df["date"].str.contains("2020-12")]
            df_2101 = df[df["date"].str.contains("2021-01")]
            df_2102 = df[df["date"].str.contains("2021-02")]
            df_2103 = df[df["date"].str.contains("2021-03")]
            df_2104 = df[df["date"].str.contains("2021-04")]
            corona_data = {'date': ["2020-03", "2020-04", "2020-05", "2020-06", "2020-07", "2020-08", "2020-09", "2020-10", "2020-11", "2020-12", "2021-01", "2021-02", "2021-03", "2021-04"],
                           'patients': [int(df_2003["gugun"].sum()), int(df_2004["gugun"].sum()), int(df_2005["gugun"].sum()), int(df_2006["gugun"].sum()),
                                        int(df_2007["gugun"].sum()), int(df_2008["gugun"].sum()), int(
                               df_2009["gugun"].sum()), int(df_2010["gugun"].sum()),
                int(df_2011["gugun"].sum()), int(df_2012["gugun"].sum()), int(df_2101["gugun"].sum()), int(df_2102["gugun"].sum()), int(df_2103["gugun"].sum()), int(df_2104["gugun"].sum())]}
            total_dic.append(corona_data)

        tt = {i: total_dic[i] for i in range(len(total_dic))}
        rt = {"target" : []}
        for i in request.data["searchList"]:
            rt["target"].append(i["juso"])

        total_data = {**df_json, **tt}
        total_data = {**total_data, **rt}
        total_data = {**total_data, **ltln_dic}

        return JsonResponse(total_data, status=200)

def midpoint(loc):
    area = []

    target_lat = 0.0
    target_lng = 0.0

    for i in loc:
        target_lat += i["lat"]
        target_lng += i["lng"]

    target_lat /= len(loc)
    target_lng /= len(loc)

    get_list = Gugun.objects.all()

    for i in get_list.iterator():
        area.append([i.signgu_nm])

    cnt = 0

    for i in get_list.iterator():

        dist = (float(i.lat) - target_lat) * (float(i.lat) - target_lat) + (
            float(i.lng) - target_lng)*(float(i.lng) - target_lng)

        area[cnt].append(dist)

        cnt += 1

    area.sort(key=lambda x: x[1])

    return area[0][0]

def nearbyArea(loc):
    area = []

    target = Gugun.objects.filter(signgu_nm=loc)
    others = Gugun.objects.all()

    for i in target.iterator():
        target_lat = float(i.lat)
        target_lng = float(i.lng)

    for i in others.iterator():
        area.append([i.signgu_nm])

    cnt = 0

    for i in others.iterator():

        dist = (float(i.lat) - target_lat) * (float(i.lat) - target_lat) + (
            float(i.lng) - target_lng)*(float(i.lng) - target_lng)

        dist = int(math.sqrt(dist) * 1000)

        area[cnt].append(dist)

        cnt += 1

    area.sort(key=lambda x: x[1])

    return area