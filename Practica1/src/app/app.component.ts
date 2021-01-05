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

  getProducts(){
    this.httpService.getPetition()
    .subscribe(products => {
      console.log(products);
    });
  }
}
