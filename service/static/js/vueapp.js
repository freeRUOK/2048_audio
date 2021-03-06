/* vueapp.js */
// * 2651688427@qq.com
/* 使用vue3做一个浏览器展示层 */
// 排行榜展示组件
let topComponent = {
  // 组件的html模板
  template: `<div v-if="plays.length !== 0"><ol><li v-for="play in plays" :key="play">{{play.name}}, {{play.score}}分, {{play.time}}秒</li></ol></div><div v-else v-html="errResult"></div>`, 
  // 组件的主要组成部分
  data () {
    return {
      plays: [],  // 玩家排行榜数据
      timer: null,   // 定时器
      errResult: `<h1>正在加载数据</h1><b>请稍后.......</b>`  // 没有排行榜时候用的元素
    }
  }, 
  // 组件绑定的时候调用
  mounted() {
    timer = setInterval(this.updatePlays, 1000 * 60)
    axios.get("/do-all")
      .then((response) => this.plays = response.data)
      .catch((error) => this.errResult = `<h1>暂无排行榜数据</h1><b>敬请期待！</b>`);
  }, 
  // 解绑组件时候调用
  unmounted() {
    clearInterval(timer);
  }, 
  methods: {
    // 请求数据， 是定时器的回调
    updatePlays() {
      axios.get(`/do-all?count=${this.plays.length}`)
        .then((response) => {
          if (response.data.length !== 0) {
            this.plays = response.data;
          }
        });
    }
  }, 
  watch: {
    // 监听数据变化， 如果发现数据有变化就重新给数据排序
    plays: function() {
      this.plays.sort((x, y) => {
        if (x.score === y.score) {
          return x.time - y.time;
        }
        else {
          return y.score - x.score;
        }
      });
    }
  }
}

// 创建vue3应用， 绑定一个html文档
window.addEventListener("load", function () {
  const vueApp = Vue.createApp({"components": {"top-component": topComponent}});
  vueApp.mount("#app");
});
