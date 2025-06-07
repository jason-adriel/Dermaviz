import { Component, ViewChild } from '@angular/core';
import { Table, TableModule } from 'primeng/table';
import { MenuComponent } from '../menu/menu.component';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { DatePipe } from '@angular/common';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';


@Component({
  selector: 'app-submissions',
  imports: [
    TableModule,
    MenuComponent,
    InputTextModule,
    ButtonModule,
    DatePipe,
    IconFieldModule,
    InputIconModule
  ],
  templateUrl: './submissions.component.html',
  styleUrl: './submissions.component.scss'
})
export class SubmissionsComponent {

  @ViewChild('submissions') tableSubmissions!: Table;

  public rowData: any[] = [
        {
      'name': "LoremIpsum"
    }
  ];
  public selectedData: any[] = [];
  public isDeleteButtonShown: boolean = false;

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private messageService: MessageService
  )
  {

  }

  protected onRowSelectChange() {
    if (this.selectedData.length > 0) {
      this.isDeleteButtonShown = true;
    } else {
      this.isDeleteButtonShown = false;
    }
  }

  protected onGlobalFilter(event: Event) {
    const input = event.target as HTMLInputElement;
    this.tableSubmissions.filterGlobal(input.value, 'contains');
  } 

  protected viewResult(data: any) {

  }

  protected addSubmission() {
    this.router.navigate(['/input']);
  }

}
