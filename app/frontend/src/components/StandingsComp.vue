<script>
import axios from "axios";
export default {
  data() {
    return {
      season: 2022,
      standings: [ [ 1, "Max Verstappen", 454 ], [ 2, "Charles Leclerc", 308 ], [ 3, "Sergio Pérez", 305 ], [ 4, "George Russell", 275 ], [ 5, "Carlos Sainz", 246 ], [ 6, "Lewis Hamilton", 240 ], [ 7, "Lando Norris", 122 ], [ 8, "Esteban Ocon", 92 ], [ 9, "Fernando Alonso", 81 ], [ 10, "Valtteri Bottas", 49 ], [ 11, "Daniel Ricciardo", 37 ], [ 12, "Sebastian Vettel", 37 ], [ 13, "Kevin Magnussen", 25 ], [ 14, "Pierre Gasly", 23 ], [ 15, "Lance Stroll", 18 ], [ 16, "Mick Schumacher", 12 ], [ 17, "Yuki Tsunoda", 12 ], [ 18, "Guanyu Zhou", 6 ], [ 19, "Alexander Albon", 4 ], [ 20, "Nicholas Latifi", 2 ], [ 21, "Nyck de Vries", 2 ], [ 22, "Nico Hülkenberg", 0 ] ],
    };
  },
  methods: {
    getStandings() {
      const path = "http://127.0.0.1:5000/standings";
      axios.get(path).then((response) => {
        console.log(response);
        if (response.status == 200) {
          this.standings = response.data.drivers;
        }
      });
    },
    sendYear(payload) {
        const path = "http://127.0.0.1:5000/standings";
        axios.post(path, payload).then((response) => {
            // this.load = false;
            this.standings = response.data.drivers;
        });
    },
    onSubmitYear(event) {
        // this.standings = [];
        this.season = parseInt(event.target.value);
        const payload = {
            year: this.season,
        };
        this.sendYear(payload);
        // this.load = true;
    },
  },
  created() {
    this.getStandings();
  },
};
</script>

<style scoped lang="scss">
.standings {
  font-family: "Roboto Mono";
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.table-standings {
  max-height: 300px;
  overflow: auto;
}
.years {
  margin-right: 1rem;
}
.standings td {
  border-left: 1px solid;
  border-right: 1px solid;
  border-bottom: 1px solid;
  padding-right: 20px;
  padding-left: 20px;
}
#title {
  padding-top: 1rem;
  padding-bottom: 1rem;
}
#header {
  border-bottom: 1px solid;
}
#driver-name {
  border-right: 1px solid;
  min-width: 150px;
}
#driver-rank {
  border-right: 1px solid;
  min-width: 50px;
}
#driver-points {
  min-width: 50px;
}
#table-driver {
  text-align: left;
}
</style>

<template>
  <h2 id="title">Standings for {{ season }} Formula One Season</h2>
  <div class="standings">
    <select class="years bg-dark-200 px-2 py-1 rounded-md" @change="onSubmitYear($event)">
      <option v-for="n in 73" :value="2023 - n" :key="2023 - n">{{ 2023 - n }}</option>
    </select>
    <div class="table-standings">
      <table>
        <tr id="header">
          <th id="driver-rank">Rank</th>
          <th id="driver-name">Driver</th>
          <th id="driver-points">Points</th>
        </tr>
        <tr v-for="(driver, index) in standings" :key="index">
          <td>{{driver[0]}}</td>
          <td id="table-driver">{{driver[1]}}</td>
          <td>{{driver[2]}}</td>
        </tr>
      </table>
    </div>
  </div>
</template>
