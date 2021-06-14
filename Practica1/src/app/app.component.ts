import { Component } from '@angular/core';
import {HttpService} from './core/http.service';
import { Entradas } from './entradas';

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
      .subscribe((this_entrada:Entradas) => {
        alert(this_entrada.message);
        console.log(this_entrada.message);
    });
  }
  recoverProducts(variable: string){
    alert("Pidiendo el producto...")
    this.httpService.recoverPetition(variable)
      .subscribe((this_entrada: Entradas) => {
        alert(this_entrada.message);
        console.log(this_entrada.message);
      });
  }
}
