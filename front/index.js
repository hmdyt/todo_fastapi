const url = "http://localhost:8000"
const post = async (endpoint, obj) => {
    res = await fetch(url + endpoint, {
        mode: 'cors',
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(obj)
    })
    return res.json()
}

const put = async (endpoint) => {
    res = await fetch(url + endpoint, {
        mode: 'cors',
        method: 'PUT',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
}

const del = async (endpoint) => {
    res = await fetch(url + endpoint, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
}

new Vue({
    el: '#app',
    data() {
        return {
            todoList: null,
            formValue: "",
        }
    },
    methods: {
        getTask: function() {
            fetch(url + "/tasks")
            .then(res => res.json())
            .then(data => this.todoList = data)
        },
        postTask: function(formValue) {
            post("/tasks", {title: formValue})
            .then(this.getTask)
        },
        markAsDone: function(id){
            put(`/tasks/${id}/done`)
            .then(this.getTask)
        },
        markAsTodo: function(id) {
            del(`/tasks/${id}/done`)
            .then(this.getTask)
        },
        deleteTask: function(id) {
            del(`/tasks/${id}`)
            .then(this.getTask)
        }
    },
    mounted() {
        this.getTask()
    }
})