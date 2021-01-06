import { Component } from '@angular/core';
import {HttpService} from './core/http.service'

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(
    private httpService: HttpService
  ){}
  title = 'Practica1';
  inputText="";
  sendOrder( variable: string ){
    alert("Message sent: "+variable);
  }

  buyProducts(variable: string){
    this.httpService.buyPetition(variable)
    .subscribe(products => {
      console.log("BUYPRODUCTS")
      //console.log(products);
    });
  }
  recoverProducts(variable: string){
    alert("Pidiendo el producto...")
    this.httpService.recoverPetition(variable)
    .subscribe(products => {
      //console.log("RECOVERPRODUCTS")
      alert(products["message"]);
      console.log(products["message"]);
    });
  }
}
