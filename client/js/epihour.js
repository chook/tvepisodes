	//global variables
	var checked_no=0;
	var data = null;
	var favoritesTable = null;
	var table = null;
	var query = null;
	var favoritesData = null;
	var userID = 'ndef';
	var userFriendsID = '';
	var currLink = "http://tvepisodes.googlecode.com/svn/trunk/client/"
	var friendsinf = 40;
	var genresinf = 60;
	var browser = navigator.appName;

	
	// Tabs
	var tabs = null;
        
	google.load("visualization", "1", {packages:["columnchart", "table" ,"barchart" , "piechart"]});	 
    function init() {
	
		if (!(gadgets.util))
			document.getElementById('NotLoggedUser').style.display = '';
				
		else		
		{		
			var req = opensocial.newDataRequest();

			req.add(req.newFetchPersonRequest(opensocial.IdSpec.PersonId.OWNER), 'owner');
  
			var ownerFriends = opensocial.newIdSpec({ "userId" : "OWNER", "groupId" : "FRIENDS" });
			var opt_params = {};
			
			req.add(req.newFetchPeopleRequest(ownerFriends, opt_params), 'ownerFriends');
	
			req.send(onLoadFriends);
		}
		
	}
	
	
	
	function loadAll(){
		tabs = new _IG_Tabs(__MODULE_ID__ );
		// When you use addDynamicTab, the tab's content is 
        // dynamically generated through the callback function. 
        tabs.addTab("News", "news_div", create_msg);
        tabs.addTab("My Shows", "epsd_div", showFavorites);
        tabs.addTab("Add", "add_div" , showAddDiv());
        tabs.addTab("Statistics", "sts_div",showSts());
		getMostPopularShows();
		//getFavorites();	
	}
       
	function showFavorites() {
		getFavorites();       	
		document.getElementById('favorites').style.display = '';
	}
	function showSts()	
	{
		document.getElementById('sts_div').style.display = '';
		getStatistics('genres' , 5);
	}

	function onLoadFriends(data) {
		var owner = data.get('owner').getData();
		var ownerFriends = data.get('ownerFriends').getData();
		
		// Set the user Id
		userID = owner.getId();

		ownerFriends.each(function(person) {
			if (person.getId()) {
				userFriendsID += person.getId() + ',' ;
    		}	    		
		});
		if (userFriendsID.length > 0)
			userFriendsID = userFriendsID.substring(0,userFriendsID.length - 1);
		
		//init all the other stuff
		loadAll();
	}
	function showAddDiv(){
		document.getElementById('search_buttons').style.display = '';
		document.getElementById('bottom_buttons').style.display = '';
		document.getElementById('most_pop').style.display = '';		
		document.getElementById('most_pop_txt').style.display = '';	
		document.getElementById('vis_results').style.display = '';
		document.getElementById('optTable').style.display = '';
		document.getElementById('main_div').style.display = '';
	}
	function getRecommended()    {
		document.getElementById('no_result_div').style.display='none';
		document.getElementById('search_error_div').style.display='none';
		document.getElementById('vis_results').style.display = 'none'; 
		document.getElementById('most_pop').style.display = 'none';		
		document.getElementById('most_pop_txt').style.display = 'none';	
		document.getElementById('recmnd_txt').style.display = 'none';			
		document.getElementById('recmnd_div').style.display = 'none';					
		document.getElementById('searching...').style.display = '';
		document.getElementById('optTable').style.display = 'none';		
		document.getElementById('bottom_buttons').style.display = 'none';
		
		UnTip();
		
		checked_no = 0;
		
		var url = 'http://epihourtesting2.appspot.com/recommend?uid=' + userID + 
				  '&friends=' + userFriendsID + '&showscount=36';
		
		query = new google.visualization.Query(url);

		// Send the query with a callback function.
		query.send(handleRecommendedQueryResponse);
	}

	function handleRecommendedQueryResponse(response)	{
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		document.getElementById('searching...').style.display = 'none';
		document.getElementById('optTable').style.display = '';		
		document.getElementById('bottom_buttons').style.display = '';
		document.getElementById('recmnd_div').style.display = '';	
		document.getElementById('recmnd_txt').style.display = '';
		document.getElementById('bottom_buttons').style.display = '';
		data = response.getDataTable();
		data.addColumn('string' , '');
		for (var j=0; j<data.getNumberOfRows(); j++){						
			data.setValue(j , 12, '<img style="cursor:hand" id="add'+data.getValue(j,0)+'" src="' + currLink + 'images/add.png" alt="Add it!" onclick="UnTip(); add_show('+data.getValue(j,0)+',id);" />');					
		}
		table = new google.visualization.Table(document.getElementById('recmnd_div'));
		var view = new google.visualization.DataView(data);
		view.hideColumns([0,2,3,4,5,6,7,8,9,10,11]); // show only the show name and the add buttons.
		if (data.getNumberOfRows()<1){
			alert('We could not find any show for you at the moment');
		} else {
			table.draw(view, {showRowNumber: false, allowHtml:true, width: 210, page: 'enable', pageSize: 3});
			google.visualization.events.addListener(table, 'select', selectRecHandler);
		}
	
		//get slider value
		getOptions();
	}
	function selectRecHandler(e) {
		var selection = table.getSelection();
		if (selection.length>0){
			for (var i = 0; i < selection.length; i++) {
				var name = data.getValue(selection[i].row, 1);
				var date = data.getValue(selection[i].row, 2);
				var seasonsNum = data.getValue(selection[i].row, 3);
				var country = data.getValue(selection[i].row, 4);
				var classification = data.getValue(selection[i].row, 5);
				var status =  data.getValue(selection[i].row, 6);
				var infoLink =  data.getValue(selection[i].row, 7);
				var airTime =  data.getValue(selection[i].row, 8);
				var airDay =  data.getValue(selection[i].row, 9);
				var recmnd =  data.getValue(selection[i].row, 10);
				if (seasonsNum != 1){
					if (status == 'Canceled/Ended')
						Tip(recmnd + ' \"'+name+ '\" was first broadcasted on '+date+'. There were '+seasonsNum+' seasons for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
					else
						Tip(recmnd + ' \"'+name+ '\" was first broadcasted on '+date+'. There are '+seasonsNum+' seasons for this show and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);						}


				else{
					if ((status == 'Canceled/Ended') || (status == 'Pilot Rejected'))
						Tip(recmnd + ' \"'+name+ '\" was first broadcasted on '+date+'. There was only '+seasonsNum+' season for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
					else
						Tip(recmnd + ' \"'+name+ '\" was first broadcasted on '+date+'. There is '+seasonsNum+' season for this show and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
				}
			}
		} else {
			UnTip();
		}
	}

    function printMostPopularShows()
    {
    		getMostPopularShows();
		document.getElementById('no_result_div').style.display='none';
		document.getElementById('search_error_div').style.display='none';
		document.getElementById('vis_results').style.display = 'none';
		document.getElementById('recmnd_div').style.display = 'none';	
		document.getElementById('recmnd_txt').style.display = 'none';
		document.getElementById('most_pop').style.display = '';		
		document.getElementById('most_pop_txt').style.display = '';
    }
	
	function getMostPopularShows()    {
		UnTip();

		checked_no = 0;
		var url = 'http://epihourtesting2.appspot.com/topShows?limit=5' + '&uid=' + userID;

		query = new google.visualization.Query(url);

		// Send the query with a callback function.
		query.send(handlePopularQueryResponse);
	
	}
  
	function handlePopularQueryResponse(response)	{
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		data = response.getDataTable();
		data.addColumn('string' , '');
		for (var j=0; j<data.getNumberOfRows(); j++){
			if (data.getValue(j,11) == '0')
				//this show is not in the user's favorites shows
				data.setValue(j , 12, '<img style="cursor:hand" id="add'+data.getValue(j,0)+'" src="' + currLink + 'images/add.png" alt="Add it!" onclick="UnTip(); add_show('+data.getValue(j,0)+',id);"\>');
			else	//this show is in the user's favorites shows		
				data.setValue(j , 12, '<img id="added'+data.getValue(j,0)+'" src="' + currLink + 'images/added.png" alt="Added!" onclick="UnTip();"\>');
		}
		table = new google.visualization.Table(document.getElementById('most_pop'));
		var view = new google.visualization.DataView(data);
		view.hideColumns([0,2,3,4,5,6,7,8,9,10,11]); // show only the show name and the add buttons.
		if (data.getNumberOfRows()<1){
			alert('there are no pop shows');
		} else {
			table.draw(view, {showRowNumber: true, allowHtml:true, width: 210, page: 'enable', pageSize: 5});
			google.visualization.events.addListener(table, 'select', selectPopHandler);
		}
		
		//get slider value
		getOptions();
	}
    function selectPopHandler(e) {

		var selection = table.getSelection();
		if (selection.length>0){
			for (var i = 0; i < selection.length; i++) {
				var name = data.getValue(selection[i].row, 1);
				var date = data.getValue(selection[i].row, 2);
				var seasonsNum = data.getValue(selection[i].row, 3);
				var country = data.getValue(selection[i].row, 4);
				var classification = data.getValue(selection[i].row, 5);
				var status =  data.getValue(selection[i].row, 6);
				var infoLink =  data.getValue(selection[i].row, 7);
				var airTime =  data.getValue(selection[i].row, 8);
				var airDay =  data.getValue(selection[i].row, 9);
				if (seasonsNum != 1){
					if (status == 'Canceled/Ended')
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There were '+seasonsNum+' seasons for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
					else
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There are '+seasonsNum+' seasons for this show and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
				}
				else{
					if ((status == 'Canceled/Ended') || (status == 'Pilot Rejected'))
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There was only '+seasonsNum+' season for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
					else
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There is '+seasonsNum+' season for this show and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
				}
			}
		} else {
			UnTip();
		}
	} 
       
    function search_episode() {
		UnTip();
		document.getElementById('no_result_div').style.display='none';
		document.getElementById('search_error_div').style.display='none';
		document.getElementById('vis_results').style.display = 'none' ;
		document.getElementById('most_pop').style.display = 'none';
		document.getElementById('most_pop_txt').style.display = 'none';			
		document.getElementById('recmnd_div').style.display = 'none';	
		document.getElementById('recmnd_txt').style.display = 'none';
		document.getElementById('searching...').style.display = '' ;
		document.getElementById('optTable').style.display = 'none';		
		document.getElementById('bottom_buttons').style.display = 'none';
		checked_no = 0;
		var url = 'http://epihourtesting2.appspot.com/searchShow?name=' + document.getElementById('srch_txt').value.toLowerCase() + '&uid='+userID;
		
		query = new google.visualization.Query(url);
		
		// Send the query with a callback function.
		query.send(handleQueryResponse);

		document.getElementById('most_pop').style.display = 'none';
		document.getElementById('searching...').style.display = '' ;
		document.getElementById('bottom_buttons').style.display = 'none';
	}
  
	function handleQueryResponse(response)	{
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		data = response.getDataTable();
		data.addColumn('string' , '');
		for (var j=0; j<data.getNumberOfRows(); j++){
			if (data.getValue(j,10) == '0')
				data.setValue(j , 11, '<img style="cursor:hand" id="add'+data.getValue(j,0)+'" src="' + currLink + 'images/add.png" alt="Add it!" onclick="UnTip(); add_show('+data.getValue(j,0)+',id);"\>');
			else	//this show is in the user's favorites shows		
				data.setValue(j , 11, '<img id="added'+data.getValue(j,0)+'" src="' + currLink + 'images/added.png" alt="Added!" onclick="UnTip();"\>');				
		}
		
		table = new google.visualization.Table(document.getElementById('vis_results'));
		var view = new google.visualization.DataView(data);
		view.hideColumns([0,2,3,4,5,6,7,8,9,10]); // show only the show name and the add buttons.
		if (data.getNumberOfRows()<1){
			document.getElementById('vis_results').style.display='none';
			document.getElementById('searching...').style.display = 'none' ;
			document.getElementById('optTable').style.display = '';		
			document.getElementById('bottom_buttons').style.display = '';
			document.getElementById('no_result_div').style.display='';
		} else {
			if ((data.getNumberOfRows() == 1) && (data.getValue(0,0) == 0)){
				document.getElementById('vis_results').style.display='none';
				document.getElementById('searching...').style.display = 'none' ;
				document.getElementById('optTable').style.display = '';		
				document.getElementById('bottom_buttons').style.display = '';
				document.getElementById('search_error_div').style.display='';
			} else {
				document.getElementById('vis_results').style.display = '' ;
				document.getElementById('searching...').style.display = 'none' ;
				document.getElementById('optTable').style.display = '';		
				document.getElementById('bottom_buttons').style.display = '';
				
				table.draw(view, {showRowNumber: true, allowHtml:true, width: 210, page: 'enable', pageSize: 5});
				google.visualization.events.addListener(table, 'select', selectSearchHandler);
			}
		}
		
		//get slider value
		getOptions();
	}
	function selectSearchHandler(e) {

		var selection = table.getSelection();
		if (selection.length>0) {
			for (var i = 0; i < selection.length; i++) {
				var name = data.getValue(selection[i].row, 1);
				var date = data.getValue(selection[i].row, 2);
				var seasonsNum = data.getValue(selection[i].row, 3);
				var country = data.getValue(selection[i].row, 4);
				var classification = data.getValue(selection[i].row, 5);
				var status =  data.getValue(selection[i].row, 6);
				var infoLink =  data.getValue(selection[i].row, 7);
				var airTime =  data.getValue(selection[i].row, 8);
				var airDay =  data.getValue(selection[i].row, 9);
				if (seasonsNum != 1){
					if (status == 'Canceled/Ended')
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There were '+seasonsNum+' seasons for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
					else
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There are '+seasonsNum+' seasons for this show and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
				} else {
					if ((status == 'Canceled/Ended') || (status == 'Pilot Rejected'))
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There was only '+seasonsNum+' season for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
					else
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There is '+seasonsNum+' season for this show and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
				}
			}
		} else {
			UnTip();
		}
	}
	
    function reset_srch_text() {
        if (document.getElementById('srch_txt').value == 'TV Show Name Here')
            document.getElementById('srch_txt').value = '';
    }
    function reset_srch() { 
        checked_no = 0;
		UnTip();

        document.getElementById('srch_txt').value = 'TV Show Name Here';
        document.getElementById('most_pop').style.display = ''; 
        document.getElementById('most_pop_txt').style.display = '';
		document.getElementById('vis_results').style.display = 'none'; 
		document.getElementById('no_result_div').style.display = 'none';
		document.getElementById('search_error_div').style.display = 'none';		
		document.getElementById('searching...').style.display = 'none';
		document.getElementById('optTable').style.display = '';		
		document.getElementById('bottom_buttons').style.display = '';
		document.getElementById('recmnd_div').style.display = 'none';	
		document.getElementById('recmnd_txt').style.display = 'none';
		data = null;
		table = null;
		query = null;
		document.getElementById('main_div').removeChild(document.getElementById('vis_results'));
		var newDiv = document.createElement("div");
		newDiv.id = "vis_results";
		document.getElementById('main_div').appendChild(newDiv);
    }
	  
	function getFavorites() {
		UnTip();
		document.getElementById('epsd_div').removeChild(document.getElementById('favorites'));
		var newDiv = document.createElement("div");
		newDiv.id = "favorites";
		document.getElementById('epsd_div').appendChild(newDiv);
		
		var url = 'http://epihourtesting2.appspot.com/getFavorites?uid='+ userID;
		document.getElementById('favorites').style.display = 'none';
		document.getElementById('getting_fav').style.display = '' ;
		document.getElementById('no_fav').style.display = 'none' ;

		var favoritesQuery = new google.visualization.Query(url);

		// Send the query with a callback function.
		favoritesQuery.send(handleFavoritesQueryResponse);
	
	}
	
	
	//convert data time format to google calendar format
	function getGoogleTimeFormat(iTime,iDate,iAddMinutes)
	{
		var myDate = new Date();
		var oStr = "";

		myDate.setHours(iTime.substr(0,2));
		myDate.setMinutes(iTime.substr(3,2));

		myDate.setDate(iDate.substr(8,2)); //set day
		myDate.setMonth(iDate.substr(5,2));
		myDate.setFullYear(iDate.substr(0,4));

		// add minutes
		myDate.setMinutes(myDate.getMinutes() + iAddMinutes);

		oStr = myDate.getFullYear() +  fixTime(myDate.getMonth()) + fixTime(myDate.getDate()) + "T" + fixTime(myDate.getHours()) + fixTime(myDate.getMinutes()) + "00Z";

		return oStr;

	}

	//add zero to time par
	function fixTime(iPar)
	{
		if (iPar < 10)
			return "0" + iPar;
		else
			return iPar;
	}	
	
	function isNumber(x) 
	{ 
	  return ( (typeof x === typeof 1) && (null !== x) && isFinite(x) );
	}

	
	function handleFavoritesQueryResponse(response)	{
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		favoritesData = response.getDataTable();
		favoritesData.addColumn('string' , '');
		favoritesData.addColumn('string' , '');
		
		// 'book it!' buttons
		var epiName;
		var epiStartDate;
		var epiEndDate;
		var epiTime;
		for (var j=0; j<favoritesData.getNumberOfRows(); j++){			
				
			epiName = favoritesData.getValue(j,1);
			epiTime = favoritesData.getValue(j,12);					
			epiStartDate = getGoogleTimeFormat(favoritesData.getValue(j,8),favoritesData.getValue(j,11),0);
			epiEndDate = getGoogleTimeFormat(favoritesData.getValue(j,8),favoritesData.getValue(j,11),epiTime);			
			
			if (favoritesData.getValue(j,11) == "Show Ended")
				favoritesData.setValue(j , 13, '<img onclick="UnTip();" id="book'+j+'" src="' + currLink + 'images/book_off.png" alt="Show Ended!" border="0" />');						
			else
				favoritesData.setValue(j , 13, '<a id="book' + j +'" onclick="UnTip()" href="http://www.google.com/calendar/event?action=TEMPLATE&text=EPI%20HOUR%20-%20' + epiName + '&dates=' + epiStartDate + '/' + epiEndDate + '&details=HAVE%20FUN!&location=TV&trp=true&sprop=&sprop=name:epi%20hour%20gadget" target="_blank"><img id="book'+j+'" src="' + currLink + 'images/book.png" alt="Book it!" border="0" /></a>');						

		
			
		}
		
		// remove! buttons
		for (var j=0; j<favoritesData.getNumberOfRows(); j++){			
			favoritesData.setValue(j , 14, '<img style="cursor:hand" id="delete'+j+'" src="' + currLink + 'images/delete.png" alt="Remove it!" onclick="UnTip(); remove_row('+favoritesData.getValue(j,0)+');" />');
		}
		
		favoritesTable = new google.visualization.Table(document.getElementById('favorites'));
		var view = new google.visualization.DataView(favoritesData);
		view.hideColumns([0,2,3,4,5,6,7,8,9,10,12]); // show only name and next air date.
		document.getElementById('getting_fav').style.display = 'none' ;
		if (favoritesData.getNumberOfRows() < 1){
			document.getElementById('getting_fav').style.display = 'none' ;
			document.getElementById('no_fav').style.display = '' ;
		} else {
			document.getElementById('getting_fav').style.display = 'none' ;
			document.getElementById('favorites').style.display = '';
			favoritesTable.draw(view, {showRowNumber: true, allowHtml:true, page: 'enable', page:'enable', width: 300, pageSize: 5});
			google.visualization.events.addListener(favoritesTable, 'select', selectFavHandler);
		}
	}
	function selectFavHandler() {
		var selection = favoritesTable.getSelection();
		if (selection.length>0){
			for (var i = 0; i < selection.length; i++) {
				var name = favoritesData.getValue(selection[i].row, 1);
				var date = favoritesData.getValue(selection[i].row, 2);
				var seasonsNum = favoritesData.getValue(selection[i].row, 3);
				var country = favoritesData.getValue(selection[i].row, 4);
				var classification = favoritesData.getValue(selection[i].row, 5);
				var status =  favoritesData.getValue(selection[i].row, 6);
				var infoLink =  favoritesData.getValue(selection[i].row, 7);
				var airTime =  favoritesData.getValue(selection[i].row, 8);
				var airDay =  favoritesData.getValue(selection[i].row, 9);	

				if (seasonsNum != 1){
					if (status == 'Canceled/Ended')
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There were '+seasonsNum+' seasons for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
					else
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There are '+seasonsNum+' seasons for this show and it\'s original country is '+country+'. The show is air on '+airDay+' , '+airTime+ ' (USA time).<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>', STICKY, true, CLOSEBTN , true,CENTERMOUSE, true, ABOVE, false , FADEIN, 500, FADEOUT, 500);
				}
				else{
					if ((status == 'Canceled/Ended') || (status == 'Pilot Rejected'))
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There was only '+seasonsNum+' season for this show (it was canceled/ended) and it\'s original country is '+country+'.<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
					else
						Tip('\"'+name+ '\" was first broadcasted on '+date+'. There is '+seasonsNum+' season for this show and it\'s original country is '+country+'. The show is air on '+airDay+' , '+airTime+ ' (USA time).<br>For more information please visit <a href='+infoLink+' target=\'_blank\'>'+infoLink+'</a>' , TITLE, '<div class=\'TitleCls\'>'+name+'</div>' , STICKY, true, CLOSEBTN , true ,CENTERMOUSE, true , ABOVE , false , FADEIN, 500, FADEOUT, 500);
				}
			}
		} else {
			UnTip();
		}
	}

	function addCallbackFunction(obj) {
		var answer = obj.text.split(" ");
		//add show
		if (answer[0] == "Add"){
			if (answer[1] != "0"){
				document.getElementById('add'+answer[1]).src = currLink + "images/added.png";
				document.getElementById('add'+answer[1]).alt = "Added!";
				document.getElementById('add'+answer[1]).onclick = "";
				getMostPopularShows();
			}

		}
		//remove show
		else{
			if (answer[1] != "0"){
				getFavorites();
				getMostPopularShows();
			}
		}
	};
	
	// add = 1, remove = 0,id_name = the field to change in the table
	function makePOSTRequest(url, postdata,remove_or_add,id_name) {
		var params = {};

		//postdata = gadgets.io.encodeValues(postdata);		// already given in the encodedValue format
		params[gadgets.io.RequestParameters.METHOD] = gadgets.io.MethodType.POST;
		params[gadgets.io.RequestParameters.POST_DATA]= postdata;
		gadgets.io.makeRequest(url, addCallbackFunction, params); 		
	};
	
    function add_show(showId,id_name) {
    	document.getElementById(id_name).src = "http://tvepisodes.googlecode.com/svn/trunk/client/adding.gif";
		var url = "http://epihourtesting2.appspot.com/addFavorite";
		
		//creating the shows to add array
		var body = "uid=" + encodeURIComponent(userID);
		body += "&sid=" + encodeURIComponent(showId);

		makePOSTRequest(url, body,1,id_name);
    }
	
	// 'aaa' is default
    function remove_row(showId){
		var answer = confirm("Are you sure you want to delete this show?")
		if (answer){      
			var url = "http://epihourtesting2.appspot.com/removeFavorite";
			var body = "uid=" + encodeURIComponent(userID);
			body += "&sid=" + encodeURIComponent(showId);

			makePOSTRequest(url, body,0,'aaa');			
		}
    }
	
    function create_msg() {
		if (userID != "ndef") {
			document.getElementById('news_div').removeChild(document.getElementById('news'));
			var newDiv = document.createElement("div");
			newDiv.id = "news";
			document.getElementById('news_div').appendChild(newDiv);
			
			var url = 'http://epihourtesting2.appspot.com/getFavorites?uid='+ userID;
			var favoritesQuery = new google.visualization.Query(url);
			
			// Send the query with a callback function.
			favoritesQuery.send(createMessagesFromFav);
		}
	}
	function createMessagesFromFav(response)	{
		var msg = new _IG_MiniMessage(__MODULE_ID__, _gel("news"));
		// date variables used for date arithmetic
		var oneMinute = 60 * 1000  // milliseconds in a minute
		var oneHour = oneMinute * 60
		var oneDay = oneHour * 24
		var oneWeek = oneDay * 7
		var tvImg1 = '<img src="' + currLink + 'images/tv1.png" />';
		var tvImg2 = '<img src="' + currLink + 'images/tv2.png" />';
		var tvImg3 = '<img src="' + currLink + 'images/tv3.png" />';
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		var msgCount = 0;
		favoritesData = response.getDataTable();
		var today = new Date();
		var yesterday = new Date();
		yesterday.setDate(yesterday.getDate()-1);

		if (favoritesData != null) {
			if (favoritesData.getNumberOfRows() <= 0) {
				document.getElementById('divNewUser').style.display = '';					
			} else {
				document.getElementById('divNewUser').style.display = 'none';	
				
				for (var i=0; i < favoritesData.getNumberOfRows(); i++) {
					var nextAirDate = favoritesData.getValue(i,11);
					var prevAirDate = favoritesData.getValue(i,10);
					var name = favoritesData.getValue(i,1);
					var airDateArray = nextAirDate.split('-');
					//messages about episodes that were broadcasted yesterday
					if (prevAirDate != null){ 
						var prevDateArray = prevAirDate.split('-');
						var prevDate = new Date();
						prevDate.setFullYear(prevDateArray[0], prevDateArray[1]-1, prevDateArray[2]);
						if (Math.ceil((yesterday - prevDate)/oneDay) == 0){
							msg.createStaticMessage(tvImg2 + " \""+name + "\" was yesterday!");
							msgCount++;
						}
					}
					//messages for the next 3 days
					var showDate = new Date();
					showDate.setFullYear(airDateArray[0] , airDateArray[1] - 1 , airDateArray[2]);
		
					var leftDays = Math.floor((showDate - today) / oneDay);
					if (leftDays == -1) {
						msg.createStaticMessage(tvImg2 + " \""+name + "\" was yesterday!");
						msgCount++;
					} else if (leftDays == 0) {
						msg.createStaticMessage(tvImg2 + " \""+name + "\" is on today!");
						msgCount++;
						} else if (leftDays == 1) {
							msg.createStaticMessage(tvImg3 + " \""+name + "\" is just a day away!");
							msgCount++;
						} else if (leftDays == 2) {
							msg.createStaticMessage(tvImg1 + " \""+name + "\" will be broadcast in "+ leftDays+" days!");
							msgCount++;
						}
				}
				if (msgCount == 0)
				// no messages
					msg.createStaticMessage("No news for your favorites shows.");
			}
		}	
    }
	function getStatistics(type , limit){
		document.getElementById('sts_div').removeChild(document.getElementById('statistics'));
		var newDiv = document.createElement("div");
		newDiv.id = "statistics";
		document.getElementById('sts_div').appendChild(newDiv);
		
		var url = 'http://epihourtesting2.appspot.com/statistics?type='+type+
				  '&limit='+limit+'&friends='+userFriendsID;

		var query = new google.visualization.Query(url);

		// Send the query with a callback function.
		if(type == 'shows'){
			query.send(handleShowsStatisticsResponse);
		}
		else{
			query.send(handleGenresStatisticsResponse);			
		}
	}
	function handleShowsStatisticsResponse(response)	{
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		var showsData = response.getDataTable();
		var showsChart = new google.visualization.BarChart(document.getElementById('statistics'));
		showsChart.draw(showsData, {legend:'none', colors :['#007FFF','#333399'], width: 240, height: 230, is3D: false , title:'Most Popular Shows', backgroundColor:'#FFFFFF',focusBorderColor:'#b4c3f6' ,axisColor:'#b4c3f6',legendBackgroundColor:'#b4c3f6'});
	}
	function handleGenresStatisticsResponse(response)	{
		if (response.isError()) {
			alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
			return;
		}
		var genresData = response.getDataTable();
		var genresChart = new google.visualization.PieChart(document.getElementById('statistics'));
		genresChart.draw(genresData, {legend:'label', width: 240, height: 230, is3D: true, title: 'Most Popular Genres', backgroundColor:'#FFFFFF',focusBorderColor:'#b4c3f6',legendBackgroundColor:'#b4c3f6'});
	}
	
	function setOptions()	{				
		if (document.getElementById('recommendations_slider').style.display == 'none') {
			document.getElementById('optId').innerHTML  = "<b>-</b> Recommendations Options:";
			document.getElementById('recommendations_slider').style.display = '';
		}
		else	{
			document.getElementById('optId').innerHTML = "<b>+</b> Recommendations Options:";
			document.getElementById('recommendations_slider').style.display = 'none';
		}
	}
	
	function saveCallbackFunction(obj) {
		document.getElementById('txtDone').style.display = '';
		window.setTimeout('hideDone()', 1200);
	}
	
	
	function postReqSaveOpt(url, postdata) {
		var params = {};

		//postdata = gadgets.io.encodeValues(postdata);		// already given in the encodedValue format
		params[gadgets.io.RequestParameters.METHOD] = gadgets.io.MethodType.POST;
		params[gadgets.io.RequestParameters.POST_DATA]= postdata;
		gadgets.io.makeRequest(url, saveCallbackFunction, params); 		
	}
	
	function getOptions()	{
		var params = {};
		var url = 'http://epihourtesting2.appspot.com/fetchUserPrefs';
		params[gadgets.io.RequestParameters.METHOD] = gadgets.io.MethodType.POST;
		params[gadgets.io.RequestParameters.POST_DATA]= 'uid=' + encodeURIComponent(userID); ;
		gadgets.io.makeRequest(url, getOptCallbackFunction, params); 		
	
	}
	
	//get friends-genres ratio value
	function getOptCallbackFunction(obj)	{
		var answer = obj.text.split(" ");

		document.getElementById('mySliderBox').style.left = answer[0] ;
		document.getElementById('mySliderBox').value = answer[0];	
	}
	
	function saveOptions()	{		
		var url = 'http://epihourtesting2.appspot.com/assignUserPrefs';
		var body = 'uid=' + encodeURIComponent(userID); 
		body += '&inf=' + encodeURIComponent(document.getElementById('mySlider').value);
		postReqSaveOpt(url, body)
		
	}
	
	
	function hideDone()	{
		document.getElementById('txtDone').style.display = 'none';
	}
	
	function entsub(event) {
	//pressing Enter will perform a search
		if (browser == "Microsoft Internet Explorer") {
			if (window.event && window.event.keyCode == 13)
				search_episode();
			else
				return true;
		}
		else{
			if (event && event.which == 13)
				search_episode();
			else
				return true;
		}
	}
  
      // Call init function to initialize and display tabs.

    		_IG_RegisterOnloadHandler(init); 
		

