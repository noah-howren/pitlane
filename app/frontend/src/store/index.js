// By Anthony Ganci and Colin Martires

/*References 
  https://www.youtube.com/watch?v=Kc-FbPSdezg
  https://blog.logrocket.com/authentication-vue-3-firebase/
*/

import { createStore } from "vuex";
// import router from "../router";
import axios from "axios";
import { auth } from "../firebase";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  updateProfile
} from "firebase/auth";

export default createStore({
  state: {
    user: {
      loggedIn: false,
      data: null
    },
    nextRace: [],
    prevRace: [],
  },
  mutations: {
    SET_LOGGED_IN(state, value) {
      state.user.loggedIn = value
    },
    SET_USER(state, data) {
      state.user.data = data
    },
    SET_UPCOMING(state, upcoming) {
      state.nextRace = upcoming.nextRace
      state.prevRace = upcoming.prevRace
    }
  },
  actions: {
    async register({ commit }, { email, password, name}) {
      const response = await createUserWithEmailAndPassword(auth, email, password)
      if (response) {
        commit('SET_USER', response.user)
        updateProfile(response.user, {
          displayName: name
        })
        console.log(response)
      } else {
        throw new Error("Unable to register user")
      }
    },
    async login({ commit }, { email, password }) {
      const response = await signInWithEmailAndPassword(auth, email, password)
      console.log(response)
      if (response) {
        commit('SET_USER', response.user)
      } else {
        throw new Error('Login Failed')
      }
    },
    async logout({ commit }) {
      await signOut(auth)
      commit('SET_USER', null)
    },
    async fetchUser({ commit }, user) {
      commit('SET_LOGGED_IN', user !== null)
      if (user) {
        commit('SET_USER', {
          displayName: user.displayName,
          email: user.email
        })
      } else {
        commit('SET_USER', null)
      }
    },
    async fetchUpcoming({ commit }) {
      try {
        const payload = {
          Offseason: 'true',
        }
        const path = "http://localhost:3001/schedule/nextprev";
        await axios.post(path ,payload).then((response) => {
          commit('SET_UPCOMING', response.data);
        })
      } catch (error) {
        alert(error);
        console.log(error);
      }
    },
  },
  getters: {
    user(state){
      return state.user
    },
    getUpcoming: (state) => {state.nextRace, state.prevRace }
  }
});
