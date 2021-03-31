<template>
  <div class="graph">
      <section class="graph__header">
        <h1 class="graph__title">추천한 장소에 대한 안내</h1>
        <h4 class="graph__description">추천 받으신 장소는 다양한 데이터를 통해 연산되어 제공합니다</h4>
      </section>
      <section class="graph__reason">
        <h4>서울시 구별 확진자에 대한 데이터입니다.</h4>
        <Barchart class="graph__chart" v-if="gugun.length"/>
        <h4>추천 받은 장소에 대한 확진자 데이터입니다.</h4>
        <Linechart class="graph__chart" v-if="recomCity.length"/>
      </section>
      <section class="graph__footer">
        <button class="graph-btn" @click="reRecom">새로운 장소 추천받기</button>
        <h4 class="footer__description">장소를 재추천 받으시려면 버튼을 누르세요</h4>
      </section>
  </div>
</template>

<script>
import Barchart from "@/components/graph/Barchart.vue"
import Linechart from "@/components/graph/LineChart.vue"

export default {
  components: {
    Barchart,
    Linechart,
  },
  computed: {
    gugun() {
      return this.$store.getters.get_gugun
    },
    recomCity() {
      return this.$store.getters.get_resultCity
    },
  },
  methods:{
    reRecom(){
      this.$store.commit('MAPCANCLE');
    }
  }


}
</script>

<style lang='scss' >
  $dark-blue: #839ba5;
  $inside-border: 2px solid $dark-blue;
  
  @mixin textLayout() {
    padding-bottom: 0.25em;
    border-bottom: 2px solid $dark-blue;
  }

  @mixin borderLayout($color) {
    border: 3px solid $color;
    border-radius: 5px;
    padding: 1rem;
  } 
  
  .graph {
    @include borderLayout(#41b6e6);
    margin-top: 1em;

    &__title {
      @include textLayout();
    }

    &__description {
      @include textLayout();
      margin-top: 0.5rem;
    }
    &__chart {
      width: 100%;
      padding: 1rem;
    }

    &__footer {
      margin-top: 2em;
      border-top: $inside-border;
      padding-top: 1em;
      display: flex;
      flex-direction: column;
      align-items: center;

      .graph-btn {
        padding: 10px 18px;
        background-color: white;
        border-radius: 5px;
        width: 30%;
        border: 2px solid #ffb6c1;
        &:hover {
          background-color: #ffb6c1;
          box-shadow: 0.5px 0.5px grey;
          color: white;
        }
      }
      .footer__description {
        color: lightslategray;
        margin-top: 0.4rem;
      }
    }
  }
</style>