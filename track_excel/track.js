var casper = require('casper').create();
var url = casper.cli.args[0];
//support xpath  firepath for firebug
var x = require('casper').selectXPath;

casper.options.timeout = casper.cli.args[1];
casper.start(url, function() {
    if (url.indexOf('express-details')>0){
        this.echo(this.getHTML());
    }
    else if (url.indexOf('17track')>0){
      // this.echo(this.getHTML());
      this.echo(this.getHTML('div#jsResultList',true));
      // this.echo(this.getHTML('ul#results',true));
    }
    else if (url.indexOf('kiees')>0)
    {
      this.echo(this.getHTML('div#channel',true));
    }
    else if (url.indexOf('i.sf-express.com')>0)
    {
      this.echo(this.getHTML());
    }
    else if(url.indexOf('chukou1')>0)
    {
      this.echo(this.getHTML("table[class='table table-bordered orders']",true));
    }
	else 
	{
	  this.echo(this.getHTML());
	}
});
            
casper.run();
