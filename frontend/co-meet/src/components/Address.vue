<template>
  <div class="address">
    <section class="location">
      <MglMap
        id="map"
        :accessToken="accessToken"
        :mapStyle.sync="mapStyle"
        v-if="mapToggle"
        @load="onMapLoaded"
      >
        <!-- 마커를 반복문을 돌면서 coordinate의 좌표를 넣는다. -->
        <div class="" v-for="(item, idx) in coordinates" :key="idx">
          <mglMarker :coordinates="coordinates[idx]" color="#ffb6c1">
            <MglPopup>
              <v-card>
                <div>만날 장소 추천지: {{ recomCity[idx].gu }}</div>
              </v-card>
            </MglPopup>
          </mglMarker>
        </div>
        <!-- <mglMarker :coordinates="coordinates[1]" color="#ffb6c1" >
            <MglPopup>
              <v-card>
                <div>Hello, This is second marker!</div>
              </v-card>
            </MglPopup>
          </mglMarker> -->
      </MglMap>
      <div class="location__wrapper" v-show="!mapToggle">
        <div class="explain">
          <h2 class="explain__title">
            약속장소에 적합한 장소를 추천해드립니다
          </h2>
          <h4 class="explain__description">
            현재 위치 또는<br />직접 현재 위치를 입력하실 수 있습니다.<br />
            <b
              >한 가지의 방법을 선택하시면, 다른 한가지 방법은 사용하실 수
              없습니다.</b
            >
          </h4>
        </div>
        <!-- 둘중에 하나의 버튼을 누르면 나머지 하나는 사라짐 -->
        <button
          href="#"
          class="location__my-location text-bold"
          @click="findCurrentLocation"
        >
          내 현재 위치
        </button>
        <div class="text-center or-text">
          <b>혹은</b>
        </div>
        <div class="search-location">
          <div v-if="addrList.length > 0">
            <v-chip
            color="pink"
              close
              close-icon="mdi-close-outline"
              v-for="(addr, index) in addrList"
              :key="index"
              @click:close="temp(index)"
              >{{ addr.juso }}</v-chip
            >
          </div>
          <v-dialog v-model="dialog" width="500">
            <template v-slot:activator="{ on, attrs }">
              <input
                type="button"
                class="btn text-bold"
                v-bind="attrs"
                v-on="on"
                value="위치 입력"
                @click="findInputLocation"
              />
            </template>
            <v-card>
              <DaumPostcode :on-complete="handleAddress" />
            </v-card>
          </v-dialog>
        </div>
        <div class="terms">
          <v-dialog
            v-model="dialogTerms"
            fullscreen
            hide-overlay
            transition="dialog-bottom-transition"
          >
            <template v-slot:activator="{ on, attrs }">
              <button
                v-bind="attrs"
                v-on="on"
                class="location__terms btn text-bold"
              >
                개인 정보 이용 동의서
              </button>
            </template>
            <v-card>
              <v-toolbar dark color="#ffb6c1">
                <v-btn icon dark @click="dialogTerms = false">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
                <v-toolbar-title>개인 정보 수집 이용 동의서</v-toolbar-title>
                <v-spacer></v-spacer>
              </v-toolbar>

              <v-container class="terms__body">
                <b>Ⅰ. 개인정보의 수집 및 이용 동의서 </b> <br />
                - 이용자가 제공한 모든 정보는 다음의 목적을 위해 활용하며, 하기
                목적 이외의 용도로는 사용되지 않습니다.<br />
                ① 개인정보 수집 항목 및 수집·이용 목적<br />
                가) 수집 항목 (필수항목)<br />
                - 주소, 전화번호(자택, 휴대전화), 이메일, 신청서에 기재된 정보
                또는 신청자가 제공한 정보<br />
                나) 수집 및 이용 목적<br />
                - 현재 위치 파악과 안전 지역 추천 진행<br />
                - 이용자의 위치 및 자격확인<br />
                - 회원 정보 자원관리<br />
                ② 개인정보 보유 및 이용기간<br />
                - 수집·이용 동의일로부터 개인정보의 수집·이용목적을 달성할
                때까지<br />
                ③ 동의거부관리<br />
                - 귀하께서는 본 안내에 따른 개인정보 수집, 이용에 대하여 동의를
                거부하실 권리가 있습니다. 다만,<br />
                귀하가 개인정보의 수집/이용에 동의를 거부하시는 경우에 장학생
                선발 과정에 있어 불이익이 발생할 수<br />
                있음을 알려드립니다<br />
                <br />
                <b>Ⅱ. 고유식별정보 처리 동의서</b><br />
                ① 고유식별정보 수집 항목 및 수집·이용 목적<br />
                가) 수집 항목 (필수항목)<br />
                - 이메일<br />
                나) 수집 및 이용 목적<br />
                - 현재 위치 파악과 안전 지역 추천 진행<br />
                - 이용자의 위치 및 자격확인<br />
                - 회원 정보 자원관리<br />
                ② 개인정보 보유 및 이용기간<br />
                - 수집·이용 동의일로부터 개인정보의 수집·이용목적을 달성할
                때까지<br />
                ③ 동의거부관리<br />
                - 귀하께서는 본 안내에 따른 개인정보 수집, 이용에 대하여 동의를
                거부하실 권리가 있습니다. 다만,<br />
                귀하가 개인정보의 수집/이용에 동의를 거부하시는 경우에 장학생
                선발 과정에 있어 불이익이 발생할 수<br />
                있음을 알려드립니다.<br />
              </v-container>
            </v-card>
          </v-dialog>

          <input
            id="agree"
            type="checkbox"
            value="agreed"
            class="terms-checkbox"
            v-model="agreed"
          />
          <label for="agree">동의</label>
        </div>
        <button href="#" class="btn terms__recom text-bold" @click="getRecom">
          약속 장소 추천 받기 !
        </button>
      </div>
    </section>

    <section class="location-list">
      <div class="list__header">
        약속 장소 리스트
      </div>
      <div v-if="city.length">
        <div class="list__contents" v-for="(item, idx) in recomCity" :key="idx">
          <div class="contents__title">{{ recomCity[idx].gu }}</div>
          <div class="contents__description">
            서울시 {{ recomCity[idx].gu }}
          </div>
        </div>
      </div>
      <!-- <div class="list__contents" v-if="gugun.length">
          <div class="contents__title">명동</div>
          <div class="contents__description">서울시 중구 명동역</div>
        </div> -->
    </section>
  </div>
</template>
<script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"></script>
<script src="https://api.mapbox.com/mapbox-gl-js/v2.1.1/mapbox-gl.js"></script>

<script>
import DaumPostcode from "vuejs-daum-postcode";
import Mapbox from "mapbox-gl";
import { MglMap, MglMarker, MglPopup } from "vue-mapbox";
import axios from 'axios';

export default {
  components: {
    DaumPostcode,
    MglMap,
    MglMarker,
    MglPopup,
  },
  data() {
    return {
      accessToken:
        "pk.eyJ1IjoiaHN5MTE4IiwiYSI6ImNrbWxibWNueDByeGkycGxzMXZmZHJ5eGUifQ.MN9N94gheL1y_QPLj1vm7w",
      mapStyle: "mapbox://styles/hsy118/ckmlk2yhknikz17qsc283g4yj",
      coordinates: [],
      // mapToggle: false,
      agreed: false,
      dialogTerms: false,
      location: "",
      dialog: false,
      selectMethod: "",
      addrList: [],
    };
  },

  methods: {
    temp(index){
      console.log(index);
      // this.addrList.pop(index);
      this.$delete(this.addrList, index);
    },
       getRecom () {
          if (this.agreed === true) {
            // 구만 보내기
            const filtering = this.location.split(' ')
            console.log(filtering[1])
            this.$store.commit('ON_SEARCHING')
            // 장소 리스트
            this.$store.dispatch("GET_RECOM", filtering[1])
            // 지도
            this.$store.dispatch("GET_CORONA_PER_CITY")
          } else {
            alert("정보 이용에 동의해주세요")
          }
       },
    async onMapLoaded(event) {
      // 도시 받은거 입력
      const data = this.$store.getters.get_result;
      // 순위들 마커 리스트에 넣고
      // this.coordinates.push([data[0].lng, data[0].lat])
      await this.putCoordinate(data);
      const asyncActions = event.component.actions;
      // 순위 보여주는 비동기 함수
      const newParams = await asyncActions.flyTo({
        center: [data[0].lng, data[0].lat],
        zoom: 11,
        speed: 0.5,
      });

      console.log(newParams);
    },
    putCoordinate: function(data) {
      this.coordinates.push([data[0].lng, data[0].lat]);
      console.log(this.coordinates);
    },
    handleAddress: function(data) {
      this.location = data.jibunAddress;
      console.log(data);
      var parseString = require('xml2js').parseString;
      var key = "9F9E4000-1B83-3B87-916E-0954B13C446B";
      var jsonTemp = {};
      var self = this;
      axios.get('http://apis.vworld.kr/jibun2coord.do?q=' + data.jibunAddress + "&format=json&apiKey=" + key)
      .then(response => {
        parseString(response.data, function(err, result){
          // console.log(result);

          // console.log(result.result.EPSG_4326_Y[0]);
          // console.log(result.result.EPSG_4326_X[0]);
          // console.log(result.result.JUSO[0]);
          jsonTemp = {
            juso: result.result.JUSO[0],
            lat : result.result.EPSG_4326_X[0],
            lng : result.result.EPSG_4326_Y[0]
          };
        self.addrList.push(jsonTemp);
        })
      })
      .catch(error => { 
        alert(error);
      })
      console.log(this.addrList);
      this.dialog = false;
    },
    findCurrentLocation() {
      console.log("click cur location");
      this.selectMethod = "currentLocation";
    },
    findInputLocation() {
      console.log("click input location");
      this.selectMethod = "inputLocation";
    },
  },
  computed: {
    mapToggle() {
      return this.$store.getters.get_mapToggle;
    },
    city() {
      return this.$store.getters.get_result;
    },
    recomCity() {
      return this.$store.getters.get_result;
    },
  },
  watch: {
    selectMethod: function() {
      const inputLocation = document.querySelector(".search-location");
      const currentLocation = document.querySelector(".location__my-location");
      const or = document.querySelector(".or-text");
      if (this.selectMethod === "currentLocation") {
        inputLocation.style.display = "none";
        or.style.display = "none";
      } else {
        currentLocation.style.display = "none";
        or.style.display = "none";
      }
    },
  },
  created() {
    this.mapbox = null;
  },
};
</script>

<style>
.explain__title,
.explain__description,
.search-location,
.terms {
  padding: 2%;
  border-bottom: 2px solid #ffb6c1;
}
.text-bold {
  font-weight: 600;
}
.address {
  margin-top: 100px;
  display: flex;
  justify-content: space-between;
}
.location {
  padding: 10px 22px;
  width: 55%;
  border: 3px solid #ffb6c1;
  border-radius: 5px;
}
.location__terms {
  margin-right: 3%;
}
.location__my-location {
  display: block;
  width: 60%;
  border: 1px solid #41b6e6;
  border-radius: 5px;
  margin: 10px auto;
  padding: 10px 0;
}
.location__my-location:hover {
  background-color: #41b6e6;
  color: #eeeeee;
  box-shadow: 0.5px 0.5px grey;
}
.search-location {
  display: flex;
  justify-content: space-evenly;
}
.location-text {
  background-color: gainsboro;
  border-radius: 5px;
  width: 65%;
  margin-right: 1em;
}
.btn {
  border: 1px solid #001871;
  border-radius: 5px;
  padding: 8px 16px;
}
.btn:hover {
  background-color: #001871;
  color: #eeeeee;
  box-shadow: 0.5px 0.5px grey;
}
.terms {
  padding: 12px;
}
.terms__recom {
  display: block;
  margin: 3% auto 0 auto;
}
.terms__body {
  padding: 2rem;
}
#map {
  width: 100%;
  height: 25em;
  border-radius: 5px;
}

/* 로케이션 리스트 ! */
.location-list {
  width: 40%;
  border: 3px solid #ec8a8a;
  border-radius: 5px;
}

.list__header {
  font-size: 12px;
  color: lightslategray;
  padding: 9px;
}
.list__contents {
  padding: 9px;
  border-bottom: 1px solid #ec8a8a;
}
.list__contents:hover {
  color: #eeeeee;
  background-color: #ec8a8a;
  box-shadow: 0.5px 0.5px grey;
}
.contents__title {
  font-weight: 600;
  font-size: 1.2em;
}
.contents__description {
  font-size: 0.9em;
}
@media screen and (max-width: 48rem) {
  .address {
    margin-top: 100px;
    display: flex;
    flex-direction: column;
  }
  .location {
    width: 100%;
    margin-bottom: 5%;
  }
  .location-list {
    width: 100%;
  }
}
</style>
