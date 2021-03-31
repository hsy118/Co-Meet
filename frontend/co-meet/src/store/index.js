import Vue from 'vue'
import Vuex from 'vuex'
import axios from "axios"

Vue.use(Vuex)

const SERVER_URL = process.env.VUE_APP_SERVER_URL;

export default new Vuex.Store({
  state: {
    searchingCity: "",
    onSearching: false,
    gugun: [],
    gugunData: [],
    recomCity: [],
    mapToggle: false,
    reRecom : false,
    accessToken: localStorage.getItem('accessToken'),
    userEmail: localStorage.getItem('email'),
    userName: localStorage.getItem('nickname'),
  },
  getters:{
    getAccessToken(state){
      return state.accessToken;
    },
    getUserEmail(state){
      return state.userEmail;
    },
    getUserName(state){
      return state.userName;
    },
    get_gugun(state) {
      return state.gugun
    },
    get_gugunData(state) {
      return state.gugunData
    },
    get_city(state) {
      return state.searchingCity
    },
    get_result(state) {
      return state.recomCity
    },
    get_mapToggle(state) {
      return state.mapToggle
    },
    get_reRecom(state){
      return state.reRecom;
    },
    get_resultCity(state) {
      return state.recomCity
    },
    get_onSearching(state) {
      return state.onSearching
    }
  },
  mutations: {
    LOGIN(state){
      state.accessToken = localStorage.getItem('accessToken');
      state.nickname = localStorage.getItem('nickname');
      state.email = localStorage.getItem('email');
    },
    LOGOUT(state){
      state.accessToken = null;
      state.userEmail = '';
      state.userName = '';
      localStorage.removeItem('accessToken');
      localStorage.removeItem('nickname');
      localStorage.removeItem('email');
    },
    MAPTOGGLE(state) {
      state.mapToggle = !state.mapToggle
    },
    MAPCANCLE(state) {
      state.mapToggle = false;
      state.gugun= [];
      state.gugunData= [];
      state.recomCity= [];
    },
    ON_SEARCHING(state) {
      state.onSearching = true
    },
    OFF_SEARCHING(state) {
      state.onSearching = false
    },
    PUT_CITY(state, city) {
      state.searchingCity = city
    },
    PUT_RESULT(state, location) {
      state.recomCity.push(location)
    },
    ON_RERECOM(state){
      state.reRecom = true;
    },
    OFF_RERECOM(state){
      state.reRecom = false;
    }
  },
  actions: {
    async GET_RECOM(context, city) {
      try {
        const res = await axios.post("https://j4a203.p.ssafy.io/api/recomm", {signgu_nm: city})
        // 검색으로 넣은 구 
        context.commit('PUT_CITY', city)
        const data = res.data
        const location = {
          lat: data.recomm_lat,
          lng: data.recomm_lng,
          gu: data.signgu_nm,
          date: data.date,
          patients: data.patients
        }
        context.commit("PUT_RESULT", location)
        context.commit("MAPTOGGLE")
        console.log(`recomcity`)
        console.log(this.state.recomCity)
      } catch(err) {
        console.log(err)
        context.commit("OFF_SEARCHING")
      }
    },
    async GET_CORONA_PER_CITY(context) {
      try {
        const res = await axios.get("https://j4a203.p.ssafy.io/api/corona-list")
        const data = res.data
        for (let key in data.gugun) {
          this.state.gugun.push(data.gugun[key])
        }
        for (let key in data.serial_number) {
          this.state.gugunData.push(data.serial_number[key])
        }
        console.log(this.state.gugun)
        console.log(this.state.gugunData)
        context.commit("OFF_SEARCHING")
        
      } catch (err) {
        console.log(err)
        context.commit("OFF_SEARCHING")
      }
    },
    LOGIN(context, user){
      context.commit("ON_SEARCHING")
      const params = new URLSearchParams();
      params.append('email', user.email);
      params.append('password', user.password);

      axios.post(`${SERVER_URL}/user/login`, params)
      .then(response => {
        localStorage.setItem('accessToken', response.data.token);
        localStorage.setItem('nickname', response.data.nickname);
        localStorage.setItem('email', response.data.email);
        context.commit('LOGIN');
        context.commit("OFF_SEARCHING")
      })
      .catch(() => {
        context.commit("OFF_SEARCHING")
      })     
    },
    LOGOUT(context, email){
      axios.get(`${SERVER_URL}/user/logout/` + email)
      .then(response => {
        console.log(response);
      })
      .catch(error => {
        alert(error);
      })

      context.commit('LOGOUT');
      // location.href = "/";
    },
  }
})
