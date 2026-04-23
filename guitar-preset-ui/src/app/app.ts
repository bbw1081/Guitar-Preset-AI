import { Component } from '@angular/core';
import { Generator } from "./components/generator/generator";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [Generator],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {}
