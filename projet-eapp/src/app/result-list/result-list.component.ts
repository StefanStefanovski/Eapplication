import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ServerService} from "../services/server.service";

@Component({
  selector: 'app-result-list',
  templateUrl: './result-list.component.html',
  styleUrls: ['./result-list.component.css']
})
export class ResultListComponent implements OnInit {


  @Input()
  public data;

  @Output() selectItem: EventEmitter<any> = new EventEmitter();

  constructor(private serverService: ServerService) { }

  ngOnInit(): void {
  }

  onClickDef(item) {
    this.selectItem.emit(item);
  }

  containsAnyDefinition() {
    return this.data.definitions.length > 0;
  }

  containsAnyDomainTerm() {
    return this.data.domainTerms.length > 0
  }

  containsAnyAssociation() {
    return this.data.associations.length > 0
  }

  loadDefinitions() {
    console.log('foo');
    this.serverService.getResult(":GET '" + this.data.query.term + "' :DEFINITIONS").subscribe(res => {
      this.data = res;
    })
  }

  mustDisplayCategories() {
    return (this.data.query.properties.length !== 1);
  }

  definitions() {
    let result = []

    for (let definition of this.data.definitions) {
      console.log(definition);
      const regexp = new RegExp("/\d\.\s/g");
      let subDefinitions = definition.split(regexp)
      console.log(subDefinitions);
      result.push(definition);
    }

    return result;
  }
}
