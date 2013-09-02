var app = app || {};

app.EventCenter = _.extend({}, Backbone.Events);

app.Player = Backbone.Model.extend({

});

app.TopPlayersCollection = Backbone.Collection.extend({
    model:app.Player,
    url:"/players",
    comparator: function(player){ return - player.get('score');}
});

app.PlayersView = Backbone.View.extend({
    el:"#players",
    events:{
        'click .select':"selectPlayer"
    },
    template: _.template($("#playersTpl").html()),
    initialize:function(){
        var that = this;
        this.collection = new app.TopPlayersCollection();
        this.listenTo(this.collection, 'sync', this.render);
        setInterval(function(){that.collection.fetch({
            error:function(){console.log('failed players');}
        });}, 1000);
    },
    render:function(){
        this.$el.html(this.template({collection:this.collection}));
    },
    selectPlayer:function(e){
        var player_id = $(e.currentTarget).attr("pid");
        $.post('/selectplayer/', {'player':player_id}).done(function(){
           app.EventCenter.trigger('player:selected');
        });
    }
});

app.User = Backbone.Model.extend({

});

app.TopUsersCollection = Backbone.Collection.extend({
    model:app.User,
    url:'/users',
    comparator: function(user){ return - user.get('score');}
});

app.UsersView = Backbone.View.extend({
    el:"#users",

    template: _.template($("#usersTpl").html()),
    initialize:function(){
        var that = this;
        this.collection = new app.TopUsersCollection();
        this.listenTo(this.collection, 'sync', this.render);
        setInterval(function(){that.collection.fetch({
            error:function(col, resp, options){console.log('failed users');console.log(resp);console.log(options);}
        })}, 1000);
    },
    render:function(){
        this.$el.html(this.template({collection:this.collection}));
    },

});

app.SelectedCollection = Backbone.Collection.extend({
    model:app.Player,
    url:"/currentplayers"
});

app.SelectedView = Backbone.View.extend({
    el:"#selected_players",
    template: _.template($("#selectedTpl").html()),
    events:{
        "click .dropbtn":"playerDrop"
    },
    initialize:function(){
        this.collection = new app.SelectedCollection();
        this.listenTo(this.collection, 'sync', this.render);
        this.listenTo(app.EventCenter, 'player:selected', this.playerSelected)
        this.collection.fetch({
            error:function(){console.log('failed selected');}
        });
    },
    render:function(){
        this.$el.html(this.template({'collection':this.collection}));
    },
    playerSelected:function(){
        this.collection.fetch({
            error:function(){console.log('failed selected select');}
        });
    },
    playerDrop:function(e){
        var player_id = $(e.currentTarget).attr("pid");

        var that = this;
        $.post("/dropplayer/", {"player":player_id}).done(function(){
                that.collection.fetch({
            error:function(){console.log('failed selected drop');}
        });
        }).fail(function(){
            alert("error dropping");
        });
    }
});