import { composeValidators } from '@angular/forms/src/directives/shared';
import { Validator } from '@angular/forms';
import { Component, OnInit, DebugElement } from '@angular/core';
import { FormGroup, FormBuilder ,Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { BoardService } from '../../services/board.service';
import { Card } from '../../models/card';
import { Board } from '../../models/board';
import { List } from '../../models/list';
import { CardService } from '../../services/card.service';
import { CardComment } from '../../models/comment';
import { Label } from '../../models/label';
import { Member } from '../../models/member';


@Component({
    moduleId: module.id,
    selector: 'card',
    templateUrl: 'card.component.html',
    styleUrls: ['card.component.css'],
    providers: [BoardService, CardService]
})


export class CardComponent implements OnInit  {

    private board: Board;
    private card: Card;
    private cards: Card[];
    private card_hash: {};
    
    private changeNameStatus: string;
    private changeListStatus: string;
    private changeLabelsStatus: string;
    private changeMembersStatus: string;
    private changeSETimeStatus: string;
    private changeDescriptionStatus: string;
    private newCommentStatus: string;
    // Blocking card statuses
    private addBlockingCardStatus: string;
    private removeBlockingCardStatus: {};
    
    /**
     * Stores the status of the edition of each comment: standby (standby),
     * asking confirmation (asking) and waiting server response (waiting)
     * */
    private editCommentStatus: {};
    
    /**
     * Stores the status of the deletion of each comment: standby (standby),
     * asking confirmation (asking) and waiting server response (waiting)
     * */
    private deleteCommentStatus: {};


    ngOnInit(): void {
        let that = this;
        this.route.params.subscribe(params => {
            let board_id = params["board_id"];
            let card_id = params["card_id"];
            that.loadBoard(board_id);
            that.loadCard(board_id, card_id);
        });
    }

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private boardService: BoardService,
        private cardService: CardService
    ) {
        this.card_hash = {};
        this.changeNameStatus = "hidden";
        this.changeListStatus = "hidden";
        this.changeLabelsStatus = "hidden";
        this.changeMembersStatus = "hidden";
        this.changeSETimeStatus = "standby";
        this.changeDescriptionStatus = "hidden";
        this.newCommentStatus = "standby";
        this.addBlockingCardStatus = "hidden";
        this.editCommentStatus = { };
        this.deleteCommentStatus = { };
        this.removeBlockingCardStatus = { };
    }

    cardHasLabel(label: Label): boolean {
        return this.card.labels.find(function(label_i){ return label_i.id == label.id }) != undefined;
    }

    cardHasMember(member: Member): boolean {
        return this.card.members.find(function(member_id){ return member_id.id == member.id }) != undefined;
    }

    /** Called when the change labels form is submitted */
    onChangeLabels(label_ids: number[]): void{
        this.cardService.changeCardLabels(this.card, label_ids).then(updated_card => {
            this.card = updated_card;
            this.changeLabelsStatus = "hidden";
        });
    }

    /** Called when the change members form is submitted */
    onChangeMembers(member_ids: number[]): void{
        this.cardService.changeCardMembers(this.card, member_ids).then(updated_card => {
            this.card = updated_card;
            this.changeMembersStatus = "hidden";
        });
    }

    /** Called when we remove a blocking card */
    onRemoveBlockingCard(blockingCard: Card){
        this.cardService.removeBlockingCard(this.card, blockingCard).then(card_response => {
            this.card.blocking_cards = card_response.blocking_cards;
            delete this.removeBlockingCardStatus[blockingCard.id];
            // We have to remove the associated comment
            // Remember that comments with the format "blocked by <card_url_in_trello>" means card-blocking
            this.card.comments = card_response.comments;
        });
    }

    addBlockingCardRightCandidate(blockingCardId: number) {
        let blocking_card_ids = {};
        for(let blocking_card of this.card.blocking_cards){
            blocking_card_ids[blocking_card.id] = true;
        }
        return this.card.id != blockingCardId && !(blockingCardId in blocking_card_ids);
    }

    /** Called when we add a blocking card */
    onAddBlockingCard(blockingCardId: number){
        console.log("onAddBlockingCard");
        let blockingCard = this.card_hash[blockingCardId];
        this.cardService.addBlockingCard(this.card, blockingCard).then(card_response => {
            this.card.blocking_cards = card_response.blocking_cards;
            // We have to update the comments
            this.card.comments = card_response.comments;
            this.addBlockingCardStatus = "hidden";
        });
    }

    /** Called when the card name change form is submitted */
    onChangeName(name: string){
        this.cardService.changeCardName(this.card, name).then(card_response => {
            this.card.name = name;
            this.changeNameStatus = "hidden";
        });
    }

    /** Called when the card description change form is submitted */
    onChangeDescription(description: string){
        this.cardService.changeCardDescription(this.card, description).then(card_response => {
            this.card.description = description;
            this.changeDescriptionStatus = "hidden";
        });
    }

    /** Called when the card S/E form is submitted */
    onSubmitSETimeForm(time_values: any) {
        let date = time_values["date"];
        let spent_time = time_values["spent_time"];
        let estimated_time = time_values["estimated_time"];
        let description = time_values["description"];
        this.cardService.addSETime(this.card, date, spent_time, estimated_time, description).then(updated_card => {
            this.card = updated_card;
            this.changeSETimeStatus = "standby";
        });
    }
    
    /** Called when the change list  form is submitted */
    onSubmitChangeList(destination_list_id: number): void {
        // If the destination list is the same as the current list of the card, do nothing
        if(this.card.list.id == destination_list_id){
            return;
        }
        // Otherwise, get the list with that index and change the list
        for(let list_index in this.card.board.lists){
            let list_i = this.card.board.lists[list_index];
            if (list_i.id == destination_list_id) {
                this.cardService.moveCard(this.card, list_i).then(updated_card => {
                    this.card = updated_card;
                    this.changeListStatus = "hidden"; 
                });
            }
        }
    }

    /** Called when creating new comment */
    onSubmitNewComment(comment_content: string): void {
        this.cardService.addNewComment(this.card, comment_content).then(comment => {
            this.card.comments = [comment].concat(this.card.comments);
            this.newCommentStatus = "standby"; 
            this.editCommentStatus[comment.id] = "standby";
            this.deleteCommentStatus[comment.id] = "standby";
        });
    }

    /** Called when editing a comment */
    onSubmitEditComment(comment: CardComment, new_content: string): void {
        this.cardService.editComment(this.card, comment, new_content).then(edited_comment => {
            comment.content = new_content;
            this.editCommentStatus[comment.id] = "standby";
        });
    }

    /** Called when deleting a comment */
    onSubmitDeleteComment(comment: CardComment): void {
        this.cardService.deleteComment(this.card, comment).then(deleted_comment => {
            this.card.comments.splice(this.card.comments.indexOf(comment), 1);
            delete this.deleteCommentStatus[comment.id];
            delete this.editCommentStatus[comment.id];
        });
    }

    onReturnToBoardSelect(): void {
      this.router.navigate([this.board.id]);
    }

    loadCard(board_id: number, card_id: number): void {
        this.cardService.getCard(board_id, card_id).then(card => {
            this.card = card;
            // Inicialization of the status of the edition or deletion or the comments of this card
            for(let comment of this.card.comments){
                this.editCommentStatus[comment.id] = "standby";
                this.deleteCommentStatus[comment.id] = "standby";
            }
            // Initialization of the status of the removal of each one of the blocking cards or this card
            for(let blocking_card of this.card.blocking_cards){
                this.removeBlockingCardStatus[blocking_card.id] = "showed";
            }
        });
    }

    loadBoard(board_id: number): void {
        this.boardService.getBoard(board_id).then(board => {
            this.board = board;
            this.card_hash = {};
            this.cards = [];
            for(let list of this.board.lists){
                for(let card of list.cards){
                    this.cards.push(card);
                    this.card_hash[card.id] = card;
                }
            }
        });
    }

}
