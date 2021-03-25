from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.http.response import JsonResponse
from api.models import Code, Fpopl, Card, CoronaData, Gugun
from .serializers import CodeSerializer, FpoplSerializer, CardSerializer, CoronaDataSerializer, CodeBodySerializer
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
import io
import urllib
import base64
# Create your views here.


class CoronaSet(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = CoronaDataSerializer

    def set_corona(self, *args, **kwargs):
        # queryset data 받기
        corona_data = CoronaData.objects.all()
        if not corona_data.exists():
            raise HttpResponse()

        # json 파일로 변환
        corona_data_list = serializers.serialize('json', corona_data)
        # # 데이터를 하루동안 저장, 자르기 편하게 queryset 형식으로
        cache.set("corona_data", corona_data, 24 * 60 * 60)

        return JsonResponse({"message": "CORONA_SUCCESS"}, status=200)


class CodeSet(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = CodeSerializer

    def set_code(self, *args, **kwargs):
        code_data = Code.objects.all()

       # json 파일로 변환
        code_data_list = serializers.serialize('json', code_data)
        # # 데이터를 하루동안 저장, 자르기 편하게 queryset 형식으로
        cache.set("code_data", code_data, 24 * 60 * 60)

        return JsonResponse({'message': 'CODE_SUCCESS'}, status=200)


class FpoplSet(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = FpoplSerializer

    def set_fpopl(self, *args, **kwargs):
        print("11")
        fpopl_data = Fpopl.objects.all()
        print("22")
       # json 파일로 변환
        fpopl_data_list = serializers.serialize('json', fpopl_data)
        # # 데이터를 하루동안 저장, 자르기 편하게 queryset 형식으로
        cache.set("fpopl_data", fpopl_data, 24 * 60 * 60)
        print("33")

        return JsonResponse({'message': 'FPOPL_SUCCESS'}, status=200)


class CoronaList(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = CoronaDataSerializer

    def get_corona_list(self, request, *args, **kwargs):
        corona_queryset = CoronaData.objects.all()
        # corona_queryset = cache.get("corona_data")

        # 구군마다 전체 분포표
        df = pd.DataFrame(
            list(corona_queryset.all().values("serial_number", "gugun")))
        df = df.groupby(["gugun"], as_index=False).count()

        df = df.drop(index=[8, 26], axis=0)  # 기타, 타시도 삭제

        corona_json = df.to_dict()

        return JsonResponse(corona_json, safe=False)


class FpoplList(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = FpoplSerializer

    def get_fpopl_list(self, request, *args, **kwargs):

        # fpopl_queryset = cache.get("fpopl_data")
        # if fpopl_queryset is None :
        fpopl_queryset = Fpopl.objects.filter(date__contains="202001")

        df = pd.DataFrame(
            list(fpopl_queryset.all().values("date", "gugun", "popl")))

        # 일자별로 합쳐고 나눠 -> 하루동안 구별 평균 유동인구수
        # 예시) 20200101 , 영등포구 , popl 합 / 컬럼수
        # 월별로 합치고 일자로 나눠 -> 한달동안 구별 평균 유동인구수
        # 예시) 202001 동일하면 popl 합 / 컬럼수(일자별)
        # 한달, 구, 평균 유동인구수
        # 구로구 => 1월 ~ 12월 평균유동인구수
        # 구별로 유동인구수를 더하고 12로 나눠 그럼 1년동안 평균 유동인구수
        # 구별 평균 유동인구수를 한표에 보여줄수 있어 이게 정확해?
        #
        # print(df)
        fpopl_json = df.to_json(orient="index", force_ascii=False)
        print("333")
        return JsonResponse(fpopl_json, safe=False)
        # return None


class FindLoc(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = CodeSerializer

    @swagger_auto_schema(request_body=CodeBodySerializer)
    def recomm_loc(self, request, *args, **kwargs):

        # 주어지는 주소 기반으로 중간지점을 가져오는 로직
        mid = midpoint(request.data['signgu_nm'])
        # 중간 지점을 기반으로 가까운 지역 리스트 조회
        nlist = nearbyArea(mid)
        # 로케이션 : lat , lng
        temp_area = nlist[0]
        print(temp_area)
        recomm_loc = Gugun.objects.filter(signgu_nm=temp_area)
        for loc in recomm_loc.iterator():
            lat = loc.lat
            lng = loc.lng
        # 첫번째 딕셔너리 완성
        loc_data = {"recomm_lat": lat, "recomm_lng" : lng, "signgu_nm" : temp_area}

        # 해당 구의 코로나 정보 뽑아오기(해당 구에 사망하였거나 아직 완치되지 않은 데이터 추출)
        target_corona_data = CoronaData.objects.filter(gugun=temp_area).exclude(discharge="퇴원")
        # 월별로 정렬
        df = pd.DataFrame(list(target_corona_data.values("gugun", "date")))
        # 먼저 일별로 정리
        df = df.groupby(by=["date"], as_index=False).count()
        # 월별로 통합 
        # print(df["date"].str.contains("2021-03")["gugun"])
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

        corona_data = {'date' : ["2020-03","2020-04","2020-05","2020-06","2020-07","2020-08","2020-09","2020-10","2020-11","2020-12","2021-01","2021-02","2021-03"],
                        'patients' :[int(df_2003["gugun"].sum()),int(df_2004["gugun"].sum()),int(df_2005["gugun"].sum()),int(df_2006["gugun"].sum()),
                                    int(df_2007["gugun"].sum()),int(df_2008["gugun"].sum()),int(df_2009["gugun"].sum()),int(df_2010["gugun"].sum()),
                                    int(df_2011["gugun"].sum()),int(df_2012["gugun"].sum()),int(df_2101["gugun"].sum()),int(df_2102["gugun"].sum()),int(df_2103["gugun"].sum())]}

        total_data = {**loc_data, **corona_data}
        
        # 해당 구의 유동인구 데이터 
        target_fpopl_data = Fpopl.objects.filter(gugun=temp_area)
        # print(target_fpopl_data)

        return JsonResponse(total_data, safe=False)


def midpoint(loc):
    return loc


def nearbyArea(loc):
    area = []

    target = Gugun.objects.filter(signgu_nm=loc)
    others = Gugun.objects.all().exclude(signgu_nm=loc)

    for i in target.iterator():
        target_lat = float(i.lat)
        target_lng = float(i.lng)

    for i in others.iterator():
        area.append([i.signgu_nm])

    cnt = 0

    for i in others.iterator():

        dist = (float(i.lat) - target_lat) * (float(i.lat) - target_lat) + (
            float(i.lng) - target_lng)*(float(i.lng) - target_lng)

        area[cnt].append(dist)

        cnt += 1

    area.sort(key=lambda x: x[1])

    area_list = []

    for i in area:
        area_list.append(i[0])

    return area_list
